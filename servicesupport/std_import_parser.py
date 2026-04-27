"""
STD Word Document Parser  —  std_import_parser.py
Place in: servicesupport/std_import_parser.py

Images are saved to MEDIA_ROOT/std_imports/<uuid>/ and referenced
as /media/std_imports/<uuid>/image_N.png — NOT base64 embedded.
This keeps the analysis HTML small (just img src tags) so it never
causes an out-of-memory error even for documents with 20+ images.
"""

import hashlib
import json
import os
import re
import uuid
import zipfile
from lxml import etree

W   = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R   = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
A   = 'http://schemas.openxmlformats.org/drawingml/2006/main'

PLACEHOLDER = re.compile(r'click\s+or\s+tap|enter\s+text', re.I)


def _save_images(docx_path, media_root):
    """
    Extract all images from the docx and save to:
        <media_root>/std_imports/<uuid>/image_N.ext

    Returns:
        img_map  : { rId → '/media/std_imports/<uuid>/image_N.ext' }
        img_dir  : the folder path (for cleanup if needed)
    """
    img_map = {}

    # Create a unique folder for this import's images
    import_id  = uuid.uuid4().hex
    img_dir    = os.path.join(media_root, 'std_imports', import_id)
    os.makedirs(img_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(docx_path, 'r') as z:
            rels_xml = z.read('word/_rels/document.xml.rels')
    except Exception:
        return img_map, img_dir

    counter = 1
    for rel in etree.fromstring(rels_xml):
        rid    = rel.get('Id', '')
        target = rel.get('Target', '')
        rtype  = rel.get('Type', '')
        if 'image' not in rtype.lower():
            continue
        try:
            with zipfile.ZipFile(docx_path, 'r') as z:
                img_bytes = z.read(f'word/{target}')
            ext       = target.rsplit('.', 1)[-1].lower() or 'png'
            filename  = f'image_{counter}.{ext}'
            file_path = os.path.join(img_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(img_bytes)
            # Store as /media/... URL path
            img_map[rid] = f'/media/std_imports/{import_id}/{filename}'
            counter += 1
        except Exception:
            pass

    return img_map, img_dir


def _sdt_plain(sdt):
    if sdt is None:
        return ''
    content = sdt.find(f'{{{W}}}sdtContent')
    if content is None:
        return ''
    lines = []
    for p in content.findall(f'.//{{{W}}}p'):
        t = ''.join(r.text or '' for r in p.findall(f'.//{{{W}}}t')).strip()
        if t:
            lines.append(t)
    return '\n'.join(lines)


def _sdt_html(sdt, img_map):
    """
    Convert rich-text SDT to HTML.
    Images become  <img src="/media/std_imports/…/image_N.png">
    — a small URL string, not base64.
    """
    if sdt is None:
        return ''
    content = sdt.find(f'{{{W}}}sdtContent')
    if content is None:
        return ''

    parts = []
    for para in content.findall(f'.//{{{W}}}p'):
        p_parts = []
        has_img = False

        for run in para.findall(f'{{{W}}}r'):
            # ── Image ──────────────────────────────────────────
            for drawing in run.findall(f'.//{{{W}}}drawing'):
                for blip in drawing.findall(f'.//{{{A}}}blip'):
                    rid = blip.get(f'{{{R}}}embed', '')
                    if rid in img_map:
                        url = img_map[rid]
                        p_parts.append(
                            f'<img src="{url}" '
                            f'style="max-width:100%;height:auto;'
                            f'margin:6px 0;border-radius:4px;">'
                        )
                        has_img = True
            # ── Text ──────────────────────────────────────────
            t_el = run.find(f'{{{W}}}t')
            if t_el is None:
                continue
            txt = (t_el.text or '').replace('<', '&lt;').replace('>', '&gt;')
            if not txt:
                continue
            rpr = run.find(f'{{{W}}}rPr')
            if rpr is not None:
                if rpr.find(f'{{{W}}}b') is not None:
                    txt = f'<strong>{txt}</strong>'
                if rpr.find(f'{{{W}}}i') is not None:
                    txt = f'<em>{txt}</em>'
                if rpr.find(f'{{{W}}}u') is not None:
                    txt = f'<u>{txt}</u>'
            p_parts.append(txt)

        s = ''.join(p_parts).strip()
        if s:
            parts.append(s if has_img else f'<p>{s}</p>')

    return ''.join(parts)


def _clean(v):
    if not v:
        return ''
    v = str(v).strip()
    return '' if PLACEHOLDER.search(v) else v


def parse_std_docx(docx_path, media_root=None):
    """
    Parse a filled STD .docx → dict of STDReport field values.

    Args:
        docx_path  : file path string or Django InMemoryUploadedFile
        media_root : settings.MEDIA_ROOT  (required for image saving)
                     If None, falls back to base64 (not recommended for
                     documents with many images).

    Returns:
        dict with keys matching STDReport model fields.
        '_img_dir' key contains the image folder path for cleanup.
    """
    # ── Handle InMemoryUploadedFile (Django upload) ───────────
    # Save to a temp file so zipfile can seek it
    import tempfile
    tmp_path = None
    if hasattr(docx_path, 'read'):
        suffix = getattr(docx_path, 'name', 'upload.docx')
        suffix = '.' + suffix.rsplit('.', 1)[-1] if '.' in suffix else '.docx'
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        for chunk in docx_path.chunks() if hasattr(docx_path, 'chunks') else [docx_path.read()]:
            tmp.write(chunk)
        tmp.close()
        tmp_path = tmp.name
        docx_path = tmp_path

    try:
        return _parse(docx_path, media_root)
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


def _parse(docx_path, media_root):
    with zipfile.ZipFile(docx_path, 'r') as z:
        doc_xml = z.read('word/document.xml')

    body   = etree.fromstring(doc_xml).find(f'{{{W}}}body')
    tables = body.findall(f'.//{{{W}}}tbl')
    if not tables:
        return {}

    # Save images to disk (returns URL map)
    if media_root:
        img_map, img_dir = _save_images(docx_path, media_root)
    else:
        # Fallback: base64 (only for dev/testing)
        import base64 as _b64
        img_map = {}
        img_dir = None
        try:
            with zipfile.ZipFile(docx_path, 'r') as z:
                rels_xml = z.read('word/_rels/document.xml.rels')
            for rel in etree.fromstring(rels_xml):
                rid = rel.get('Id',''); target = rel.get('Target','')
                if 'image' not in rel.get('Type','').lower(): continue
                try:
                    with zipfile.ZipFile(docx_path, 'r') as z:
                        data = z.read(f'word/{target}')
                    ext = target.rsplit('.',1)[-1].lower()
                    mime = {'png':'image/png','jpg':'image/jpeg','jpeg':'image/jpeg'}.get(ext,'image/png')
                    img_map[rel.get('Id','')] = f"data:{mime};base64,{_b64.b64encode(data).decode()}"
                except: pass
        except: pass

    rows = tables[0].findall(f'{{{W}}}tr')

    def row_sdts(ri):
        return rows[ri].findall(f'{{{W}}}sdt') if ri < len(rows) else []

    def plain(ri, si=0):
        s = row_sdts(ri)
        return _clean(_sdt_plain(s[si])) if si < len(s) else ''

    def tc_html(ri, tci=0):
        if ri >= len(rows): return ''
        tcs = rows[ri].findall(f'{{{W}}}tc')
        if tci >= len(tcs): return ''
        sdt = tcs[tci].find(f'{{{W}}}sdt')
        return _sdt_html(sdt, img_map) if sdt is not None else ''

    # Application — R07 tc[1] plain text
    app_val = ''
    if 7 < len(rows):
        r7_tcs = rows[7].findall(f'{{{W}}}tc')
        if len(r7_tcs) > 1:
            app_val = _clean(''.join(
                r.text or '' for r in r7_tcs[1].findall(f'.//{{{W}}}t')
            ))

    # Hours — R08 tc[5] or tc[6]
    hours_val = '0'
    if 8 < len(rows):
        r8_tcs = rows[8].findall(f'{{{W}}}tc')
        for tci in [6, 5]:
            if tci < len(r8_tcs):
                v = _clean(''.join(r.text or '' for r in r8_tcs[tci].findall(f'.//{{{W}}}t')))
                if v.isdigit():
                    hours_val = v
                    break

    data = {
        'subject':               plain(0, 0),
        'product':               plain(1, 0),
        'content_type':          plain(1, 1) or 'Content/Solution',
        'controller_model':      plain(2, 0),
        'controller_sl_no':      plain(2, 1),
        'rm_model':              plain(3, 0),
        'rm_sl_no':              plain(3, 1),
        'machine_model':         plain(4, 0),
        'machine_sl_no':         plain(4, 1),
        'machine_tool_builder':  plain(5, 0),
        'configuration':         plain(5, 1),
        'end_user':              plain(6, 0),
        'application':           app_val,
        'mr_no':                 plain(8, 0),
        'visits_count':          plain(8, 1),
        'hours_count':           hours_val,
        'repeat_visit_reason':   plain(9,  0),
        'reason_for_subject':    plain(10, 0),
        'problem_reported':      plain(11, 0),
        'problem_observation':   plain(12, 0),
        'problem_suspected':     plain(13, 0),
        'problem_history':       plain(14, 0),
        'external_disturbance':  plain(15, 0),
        'occurrence_count':      plain(16, 0),
        'diagnosis_info':        plain(17, 0),
        # Rich text — images are small URL strings now
        'analysis':              tc_html(18, 0),
        'solution':              tc_html(19, 0),
        'additional_info':       '',
        'parts_used_json':       '[]',
        '_img_dir':              img_dir,    # folder to clean up on error
    }

    # Additional info — tables[1]
    if len(tables) > 1:
        add_sdts = tables[1].findall(f'.//{{{W}}}sdt')
        if add_sdts:
            html = _sdt_html(add_sdts[0], img_map)
            plain_text = re.sub('<[^>]+>', '', html)
            data['additional_info'] = '' if PLACEHOLDER.search(plain_text) else html

    # Parts — nested table in R20
    parts_list = []
    if 20 < len(rows):
        r20_tcs = rows[20].findall(f'{{{W}}}tc')
        if r20_tcs:
            for nested_tbl in r20_tcs[0].findall(f'.//{{{W}}}tbl'):
                for pr in nested_tbl.findall(f'{{{W}}}tr')[1:]:
                    ptcs = pr.findall(f'{{{W}}}tc')
                    if len(ptcs) >= 3:
                        spec = _clean(''.join(r.text or '' for r in ptcs[0].findall(f'.//{{{W}}}t')))
                        qty  = _clean(''.join(r.text or '' for r in ptcs[1].findall(f'.//{{{W}}}t')))
                        rsn  = _clean(''.join(r.text or '' for r in ptcs[2].findall(f'.//{{{W}}}t')))
                        if spec:
                            parts_list.append({'spec': spec, 'qty': qty, 'reason': rsn})
    data['parts_used_json'] = json.dumps(parts_list)

    # Sign-off names
    for tbl in reversed(tables):
        tbl_rows = tbl.findall(f'{{{W}}}tr')
        for i, row in enumerate(tbl_rows):
            texts = [''.join(r.text or '' for r in tc.findall(f'.//{{{W}}}t'))
                     for tc in row.findall(f'{{{W}}}tc')]
            if any('Prepared' in t and 'by' in t.lower() for t in texts):
                if i + 1 < len(tbl_rows):
                    ntcs = tbl_rows[i+1].findall(f'{{{W}}}tc')
                    if ntcs:
                        data['_prepared_by_name'] = ''.join(
                            r.text or '' for r in ntcs[0].findall(f'.//{{{W}}}t')
                        ).strip()
                    if len(ntcs) > 1:
                        data['_reviewed_by_name'] = ''.join(
                            r.text or '' for r in ntcs[1].findall(f'.//{{{W}}}t')
                        ).strip()
                break

    # Numeric normalisation
    try:
        data['visits_count'] = int(str(data['visits_count']).strip() or 1)
    except (ValueError, TypeError):
        data['visits_count'] = 1
    try:
        data['hours_count'] = int(str(data['hours_count']).strip() or 0)
    except (ValueError, TypeError):
        data['hours_count'] = 0

    # Defaults
    for f in ('subject','product','controller_model','controller_sl_no',
              'rm_model','rm_sl_no','machine_model','machine_sl_no',
              'machine_tool_builder','configuration','end_user','application',
              'mr_no','repeat_visit_reason','reason_for_subject',
              'problem_reported','problem_observation','problem_suspected',
              'problem_history','external_disturbance','occurrence_count',
              'diagnosis_info','analysis','solution','additional_info'):
        data.setdefault(f, '')

    return data