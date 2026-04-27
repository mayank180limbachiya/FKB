from typing import _SpecialForm
from django.db import models
from django.db.models.base import Model

# from django.db.models.deletion import CASCADE
from django.db.models.fields import EmailField
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User,AbstractUser
import os
from django.urls import reverse

#for no of visits
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# supports image upload
from ckeditor_uploader.fields import RichTextUploadingField  

# Create your models here.


class product_type(models.Model):
    product = models.CharField(max_length=20, unique=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product}"


class system_types(models.Model):
    product_name = models.ForeignKey(
        product_type, on_delete=models.CASCADE, related_name="product_details"
    )
    system_names = models.CharField(max_length=20)
    nick_names = models.CharField(max_length=10, default="None")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            "product_name",
            "system_names",
        )

    def __str__(self):
        return f"{self.system_names} | {self.product_name}"


class alarm_detail(models.Model):
    system_type = models.ForeignKey(
        system_types, on_delete=models.CASCADE, related_name="Alarm_system"
    )
    alarm_number = models.CharField(max_length=20)
    alarm_description = models.TextField(max_length=100)
    manual_name_number = models.TextField(
        max_length=400, default="not found", blank=True, null=True
    )
    alarm_data = RichTextField(max_length=500, blank=True, null=True)
    special_tips = RichTextField(max_length=400, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


class alarm_report(models.Model):
    alarm = models.ForeignKey(
        alarm_detail, on_delete=models.CASCADE, related_name="alarm_info"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_data")
    date = models.DateTimeField()
    report = models.CharField(max_length=200)
    report_flag = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user | self.alarm | self.report_flag}"


class manual(models.Model):
    Product_name = models.ForeignKey(
        system_types, on_delete=models.CASCADE, related_name="manual_system"
    )
    Manual_number = models.CharField(max_length=100, blank=True, null=True)
    Manual_Name = models.CharField(max_length=100, blank=True, null=True)
    Manual_storage = models.FileField(upload_to="uploads/manual/")
    comments = models.CharField(max_length=100, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


class led(models.Model):
    Product_name = models.ForeignKey(
        system_types, on_delete=models.CASCADE, related_name="led_system"
    )
    pdf_name = models.CharField(max_length=100, blank=True, null=True)
    pdf_storage = models.FileField(upload_to="uploads/alarm_led/")
    comments = models.CharField(max_length=100, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


CHOICES = (("Training", "Training"), ("Procedure", "Procedure"))


class Training_model(models.Model):
    Product_name = models.ForeignKey(
        product_type, on_delete=models.CASCADE, related_name="Training_product"
    )
    System_name = models.ForeignKey(
        system_types, on_delete=models.CASCADE, related_name="Training_system"
    )
    Training_Name = models.CharField(max_length=100, blank=True, null=True)
    Training_details = models.CharField(max_length=300, blank=True, null=True)
    Training_storage = models.FileField(upload_to="uploads/training/")
    Type = models.CharField(max_length=20, choices=CHOICES, default="Training")
    comments = models.CharField(max_length=100, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


class specification(models.Model):
    parentspec = models.CharField(max_length=55)
    parentname = models.CharField(max_length=100, blank=True, null=True)
    level = models.CharField(max_length=3, blank=True, null=True)
    spec_parent = models.CharField(max_length=50, blank=True, null=True)
    spec_PartsName = models.CharField(max_length=100, blank=True, null=True)
    childspec = models.CharField(max_length=50, blank=True, null=True)
    childname = models.CharField(max_length=100, blank=True, null=True)
    qty = models.IntegerField(blank=True, null=True)
    remarks = models.CharField(max_length=50, blank=True, null=True)
    level_1 = models.CharField(max_length=50, blank=True, null=True)
    hierarchy = models.CharField(max_length=100, blank=True, null=True)
    stockrank = models.CharField(max_length=5, blank=True, null=True)
    mainte_level = models.CharField(max_length=5, blank=True, null=True)
    SpecialSpec = models.CharField(max_length=5, blank=True, null=True)
    RegisteredDate = models.CharField(max_length=20, blank=True, null=True)
    TerminatedDate = models.CharField(max_length=20, blank=True, null=True)
    spare_type = models.CharField(max_length=3, blank=True, null=True)
    old = models.CharField(max_length=3, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


class equ(models.Model):
    spec = models.CharField(max_length=50, blank=False)
    discription = models.CharField(max_length=70, blank=True, null=True)
    reuse = models.BooleanField(blank=True, null=True)
    info = models.CharField(max_length=100, blank=True, null=True)
    equspec = models.CharField(max_length=100, blank=True, null=True)
    srno = models.CharField(max_length=50, blank=True, null=True)
    trno = models.CharField(max_length=50, blank=True, null=True)
    remark = models.CharField(max_length=150, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


class requesttype(models.Model):
    request = models.CharField(max_length=30)  # char form which screen
    requestadd = models.CharField(max_length=30)  # for which data request
    shortdetail = models.CharField(max_length=50)
    details = models.CharField(max_length=200)  # In details  discription
    flag = models.BooleanField(default=False)  # request completed
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # request user
    date = models.DateTimeField()  # request add date
    closedate = models.DateTimeField(blank=True, null=True)  # request completed date
    updated_at = models.DateTimeField(auto_now=True)


class std(models.Model):
    Std_name = models.CharField(max_length=150)
    System_type = models.ForeignKey(system_types, on_delete=models.CASCADE)
    MTB_name = models.CharField(max_length=100, blank=True, null=True)
    Machine_model = models.CharField(max_length=100, blank=True, null=True)
    problem_solved = RichTextField(max_length=1000, blank=True, null=True)
    special_comments = models.CharField(
        max_length=150,
        null=True,
        blank=True,
    )
    Part_used = models.CharField(
        max_length=500,
        null=True,
        blank=True,
    )
    file = models.FileField(upload_to="uploads/STD/")
    updated_at = models.DateTimeField(auto_now=True)

class analytics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    page = models.CharField(max_length=30)
    ip = models.CharField(max_length= 70,null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True)


class spec_details(models.Model):
    spec_no = models.CharField(max_length=50)
    description = models.CharField(max_length=100,null=True,blank=True)
    description_local= models.CharField(max_length=100,null=True,blank=True)
    photo= models.ImageField(upload_to='uploads/images/',null=True,blank=True)
    weight = models.IntegerField(null=True,blank=True)
    hsn = models.IntegerField(null=True,blank=True)
    comments = models.CharField(max_length=200,null=True,blank=True)
    large_category = models.ForeignKey(product_type,on_delete=models.CASCADE,null=True,blank=True)
    repairable = models.BooleanField(default=False) 
    exchangeable = models.BooleanField(default=False) 
    consumable = models.BooleanField(default=False) 
    discontinued = models.BooleanField(default=False) 
    def __str__(self):
        return f"{self.spec_no}"
    def serialize(self):
        return {
            "id": self.id,
            "spec_no": self.spec_no,
            "weight": self.weight,
            "photo": self.photo.url,
        }
    
class links(models.Model):
    name = models.CharField(max_length=20)
    link_name = models.CharField(max_length=30)
    def __str__(self):
        return f"{self.name}"

class UserData(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    preference_link = models.ManyToManyField(links)

class Serial_Number(models.Model):
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    serial_no = models.CharField(max_length=13)
    add_text = models.CharField(max_length=150)
    updated_at = models.DateTimeField(auto_now=True)

class Plant(models.Model):
    name = models.CharField(max_length=13)
    code = models.CharField(max_length=10)
    short_name = models.CharField(max_length=4)
    def __str__(self):
        return f"{self.name} | {self.code} | {self.short_name}"

class Storage_loc(models.Model):
    storage_location = models.CharField(max_length=6)
    name = models.CharField(max_length=6)
    def __str__(self):
        return f"{self.storage_location} | {self.name}"

class Stock(models.Model):
    material = models.ForeignKey(spec_details,on_delete=models.DO_NOTHING)
    plant = models.ForeignKey(Plant,on_delete=models.DO_NOTHING,null=True,blank=True)
    storage = models.ForeignKey(Storage_loc,on_delete=models.DO_NOTHING,null=True,blank=True)
    special_stock = models.CharField(max_length=5,null=True,blank=True)
    special_stock_number = models.CharField(max_length=30,null=True,blank=True)
    available = models.IntegerField(null=True,blank=True)
    transit =models.IntegerField(null=True,blank=True)
    returns =models.IntegerField(null=True,blank=True)
    created_date = models.DateTimeField(auto_now_add=True)


PRODUCT_CHOICES = (
    ("CNC",     "CNC"),
    ("Servo",   "Servo"),
    ("Robot",   "Robot"),
    ("RM",      "RM"),
    ("Robocut", "Robocut"),
    ("Robodrill","Robodrill"),
    ("Roboshot","Roboshot"),
    ("Laser",   "Laser"),
    ("Other",   "Other"),
)
 
CONTENT_TYPE_CHOICES = (
    ("Content/Solution", "Content/Solution"),
    ("Others",           "Others"),
)
 
STD_STATUS_CHOICES = (
    ("draft",    "Draft"),        # engineer writing
    ("submitted","Submitted"),    # sent to reviewer
    ("approved", "Approved"),     # reviewer approved
    ("rejected", "Rejected"),     # reviewer sent back
    ("published","Published"),    # visible to all engineers
)
 
 
class STDReport(models.Model):
    """
    Service Technical Discussion Report.
    Maps exactly to the Word template used by engineers.
    """
 
    # ── Header fields ──────────────────────────────────────────
    subject             = models.CharField(max_length=200)
    product             = models.CharField(max_length=20, choices=PRODUCT_CHOICES)
    content_type        = models.CharField(max_length=30, choices=CONTENT_TYPE_CHOICES,
                                            default="Content/Solution")
 
    # Equipment identification
    controller_model    = models.CharField(max_length=50, blank=True, null=True)
    controller_sl_no    = models.CharField(max_length=50, blank=True, null=True)
    machine_model       = models.CharField(max_length=50, blank=True, null=True)
    machine_sl_no       = models.CharField(max_length=50, blank=True, null=True)
    rm_model            = models.CharField(max_length=50, blank=True, null=True,
                                            verbose_name="Laser/RO/RM Model")
    rm_sl_no            = models.CharField(max_length=50, blank=True, null=True,
                                            verbose_name="Laser/RO/RM Sl. No.")
    machine_tool_builder= models.CharField(max_length=100, blank=True, null=True)
    configuration       = models.CharField(max_length=100, blank=True, null=True)
    end_user            = models.CharField(max_length=150, blank=True, null=True)
    application         = models.CharField(max_length=100, blank=True, null=True)
    installation_date   = models.DateField(blank=True, null=True)
 
    # MR / Visit info
    mr_no               = models.CharField(max_length=50, blank=True, null=True,
                                            verbose_name="MR No.")
    mr_review           = models.CharField(max_length=100, blank=True, null=True)
    is_multiple_visit   = models.BooleanField(default=False)
    visits_count        = models.PositiveSmallIntegerField(default=1)
    hours_count         = models.PositiveSmallIntegerField(default=0)
    repeat_visit_reason = models.TextField(max_length=500, blank=True, null=True)
 
    # ── Problem description ─────────────────────────────────────
    reason_for_subject  = models.TextField(
        max_length=500, help_text="Why are you presenting this subject?")
    problem_reported    = models.TextField(
        max_length=500, verbose_name="Problem as reported by End-user")
    problem_observation = models.TextField(
        max_length=1000, verbose_name="Observation of the problem with detailed description")
    problem_suspected   = models.TextField(
        max_length=500, verbose_name="Problem suspected by FSE/SRC")
    problem_history     = models.TextField(
        max_length=500, blank=True, null=True, verbose_name="History of the problem")
    external_disturbance= models.TextField(
        max_length=300, blank=True, null=True,
        verbose_name="Was there any specific external disturbance?")
    occurrence_count    = models.TextField(
        max_length=200, blank=True, null=True,
        verbose_name="How many times has it occurred?")
    diagnosis_info      = models.TextField(
        max_length=1000, blank=True, null=True,
        verbose_name="Diagnosis information as per manual")
 
    # ── Rich text sections (CKEditor with image upload) ─────────
    analysis            = RichTextUploadingField(
        blank=True, null=True,
        verbose_name="How was the problem analyzed?",
        help_text="Describe step-by-step analysis. You can paste/insert images.")
    solution            = RichTextUploadingField(
        blank=True, null=True,
        verbose_name="How was the Problem Solved?")
    additional_info     = RichTextUploadingField(
        blank=True, null=True,
        verbose_name="Any additional information")
 
    # ── Parts used (stored as JSON text) ────────────────────────
    # Format: [{"spec": "A20B-1111", "qty": 1, "reason": "..."}, ...]
    parts_used_json     = models.TextField(
        blank=True, null=True,
        verbose_name="Parts replaced (JSON)",
        help_text="Managed by form UI — do not edit manually")
 
    # ── Reviewer section ────────────────────────────────────────
    applicable_models   = models.TextField(max_length=300, blank=True, null=True)
    useful_telephonic   = models.BooleanField(null=True, blank=True,
                            verbose_name="Content useful for Telephonic Support?")
    supports_mttr       = models.BooleanField(null=True, blank=True,
                            verbose_name="Supports MTTR?")
    special_tool        = models.TextField(max_length=300, blank=True, null=True,
                            verbose_name="Any Special Tool used for Troubleshooting")
    alternate_process   = models.TextField(max_length=500, blank=True, null=True,
                            verbose_name="Any alternate process to troubleshoot")
    reviewer_remarks    = models.TextField(max_length=500, blank=True, null=True)
 
    # ── Workflow ─────────────────────────────────────────────────
    status              = models.CharField(max_length=15, choices=STD_STATUS_CHOICES,
                                            default="draft")
    prepared_by         = models.ForeignKey(User, on_delete=models.CASCADE,
                                             related_name="std_prepared")
    reviewed_by         = models.ForeignKey(User, on_delete=models.SET_NULL,
                                             null=True, blank=True,
                                             related_name="std_reviewed")
    presented_by        = models.ForeignKey(User, on_delete=models.SET_NULL,
                                             null=True, blank=True,
                                             related_name="std_presented")
    st_reviewer         = models.ForeignKey(User, on_delete=models.SET_NULL,
                                             null=True, blank=True,
                                             related_name="std_st_review")
 
    # ── System tracking ──────────────────────────────────────────
    system_type         = models.ForeignKey(
        "system_types", on_delete=models.SET_NULL, null=True, blank=True)
    submitted_at        = models.DateTimeField(null=True, blank=True)
    approved_at         = models.DateTimeField(null=True, blank=True)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)
 
    class Meta:
        ordering        = ["-created_at"]
        verbose_name    = "STD Report"
        verbose_name_plural = "STD Reports"
 
    def __str__(self):
        return f"STD-{self.id:04d} | {self.subject[:60]}"
 
    @property
    def std_number(self):
        """e.g. STD-2026-0012"""
        return f"STD-{self.created_at.year}-{self.id:04d}"
 
    @property
    def parts_list(self):
        """Returns list of dicts from JSON field."""
        import json
        if self.parts_used_json:
            try:
                return json.loads(self.parts_used_json)
            except Exception:
                return []
        return []
 
 
class STDApprovalLog(models.Model):
    """
    Audit trail — every status change is recorded here.
    """
    report      = models.ForeignKey(STDReport, on_delete=models.CASCADE,
                                     related_name="approval_log")
    action      = models.CharField(max_length=20)   # submitted / approved / rejected / published
    actor       = models.ForeignKey(User, on_delete=models.CASCADE)
    comment     = models.TextField(max_length=500, blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ["created_at"]
 
    def __str__(self):
        return f"{self.report} → {self.action} by {self.actor}"
  