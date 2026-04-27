from django.shortcuts import render , get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
# url handling
from urllib.parse import quote
import re ,csv

#email 
from django.core.mail import send_mail
from django.conf import settings

# for Paginator << first Pre 1,2,3,4,5 Next Last >>
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# from tab lib import Dataset #for data read
from django.db.models import Q
import datetime

#for Photo API
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

from .models import STDReport, STDApprovalLog

import servicesupport
from .models import (
    alarm_detail,
    led,
    equ,
    product_type,
    specification,
    system_types,
    requesttype,
    manual,
    Training_model,
    analytics,
    spec_details,
    Serial_Number,
    Stock,
    STDReport, 
    STDApprovalLog
)

from .std_import_parser import parse_std_docx

def index(request):
    return render(
        request,
        "servicesupport/Index.html",
        {"flag":1},
    )


def login_view(request):
    if request.method == "POST":
        # user name data
        username = (request.POST["username"]).lower()
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            messages.success(request, f"Welcome {user.first_name}")
            login(request, user)
            return render(
                request,
                "servicesupport/index.html",
                {
                    "flag": 1,
                },
            )
        else:
            messages.error(
                request, "Wrong User ID or Password - for support contact Admin"
            )
            return render(
                request,
                "servicesupport/login.html",
                {
                    "flag": 12,
                },
            )
    else:
        return render(
            request,
            "servicesupport/login.html",
            {
                "flag": 12,
            },
        )

@login_required
def changepassword(request):
    if request.method == "POST":
        # user name data
        username = request.user
        old_password=request.POST["old_password"]
        new_password = request.POST["new_password"]
        re_password = request.POST["renew_password"]
        user_details = User.objects.get(username=username)
        if user_details.check_password(old_password):
            if new_password.strip() == re_password.strip():
                user_details.set_password(new_password)
                user_details.save()
                messages.success(request,"Password Change Successfully")
                logout(request)
                return render(
                request,
                "servicesupport/login.html",
                {
                    "flag": 1,
                },
            )
            else: 
                messages.error(request,"New Password & Renew Password should be same")
                return render(
                request,
                "servicesupport/changepassword.html",
                {
                    "flag": 12,
                },
            )
        else:
            messages.error(request,"Kindly Enter correct OLD PASSWORD")
            return render(
                request,
                "servicesupport/changepassword.html",
                {
                    "flag": 12,
                },
            )
    else:
        return render(
            request,
            "servicesupport/changepassword.html",
            {
                "flag": 12,
            },
        )

# to check Valid mail id
def Email_check(email):
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
    if re.fullmatch(regex, email):
        return True
    else:
        return False

def add_analytics(user_name,page_name,request):
    if not user_name.is_superuser:
        data = analytics(
                    user=user_name,
                    page=page_name.lower(),
                    updated_at = datetime.datetime.now(),
                    ip= get_client_ip(request),
                )
        data.save()

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def bad_request(request, *args, **argv):
    return render(
        request,
        "servicesupport/404.html",
        {
            "flag": 12,
        },
    )


def register(request):
    user_data = {"username": None, "email": None, "first": None, "last": None}
    if request.method == "POST":
        username = request.POST["username"].lower()
        email = request.POST["email"]
        first = request.POST["first"]
        last = request.POST["last"]
        user_data = {"username": username, "email": email, "first": first, "last": last}
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            messages.error(request, "Passwords must match.")
            return render(
                request,
                "servicesupport/register.html",
                {
                    "flag": 12,
                    "user_data": user_data,
                },
            )
        if Email_check(email) == False:
            messages.error(request, "Enter Valid Mail id")
            return render(
                request,
                "servicesupport/register.html",
                {
                    "flag": 12,
                    "user_data": user_data,
                },
            )
        if len(username) < 3:
            messages.error(request, "Kindly more than 3 char user name")
            return render(
                request,
                "servicesupport/register.html",
                {
                    "flag": 12,
                    "user_data": user_data,
                },
            )
        if len(username) == 0:
            messages.error(request, "Kindly enter First Name")
            return render(
                request,
                "servicesupport/register.html",
                {
                    "flag": 12,
                    "user_data": user_data,
                },
            )
        # Attempt to create new user
        try:
            user = User.objects.create_user(
                username,
                email,
                password,
                first_name=first.lower(),
                last_name=last.lower(),
            )
            user.save()
        except IntegrityError:
            messages.error(request, "Username already taken.")
            return render(
                request,
                "servicesupport/register.html",
                {
                    "flag": 12,
                    "user_data": user_data,
                },
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(
            request,
            "servicesupport/register.html",
            {
                "flag": 12,
            },
        )


def lostpassword(request):
    if request.method == "POST":
        # user name data
        email = request.POST["email"]
        if User.objects.filter(email= email).exists():
            send_mail("Password Reset Request","You New Password is Fanuc@123",'settings.EMAIL_HOST_USER',[email])
            messages.success(request, "New Password Send to Your mail ID, Not received contact IT support")
            u= User.objects.get(email__exact=email)
            u.set_password('Fanuc@123')
            u.save()
            return render(
                request,
                "servicesupport/login.html",
                {
                    "flag": 12,
                },
                )
        else:    
            messages.error(request, "Your mail id is not available, Enter Correct Mail or Contact IT team")
    return render(
        request,
        "servicesupport/lostpassword.html",
        {
            "flag": 12,
        },
    )


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "logout Success")
    return render(
        request,
        "servicesupport/index.html",
        {
            "flag": 13,
        },
    )


@login_required
def profile(request):
    user = request.user
    user_details = User.objects.get(username=user)
    links_data = links.objects.all()
    if request.method == "POST" and request.user.is_authenticated:
        Data_1 = request.POST["1"]
        Data_2 = request.POST["2"]
        Data_3 = request.POST["3"]
        Data_4 = request.POST["4"]
        Data_5 = request.POST["5"]
        list_data=[Data_1,Data_2,Data_3,Data_4,Data_5]  
    print(user_details)
    return render(
        request,
        "servicesupport/profile.html",
        {
            "flag": 13,
            'user_details':user_details,
            'links':links_data,
            'list':list_data
        },
    )



@login_required
def std(request):
    return render(
        request,
        "servicesupport/std.html",
        {
            "flag": 3,
        },
    )


@login_required
def training(request):
    if 'Engineer' not in list(request.user.groups.values_list('name',flat = True)):
        messages.error(
                request, "Permission required To visit- Engineer or Manager"
            )
        return render(
            request,
            "servicesupport/index.html",
            {
                "flag": 1,
            },
        )

    add_analytics(request.user,"training",request)
    page_obj = None
    User_input = {"Training": None, "Product": None, "limit": None, "line_index_adder":None}
    search_data = Training_model.objects.none()
    Product = Training_model.objects.values_list("Product_name", flat=True).distinct()
    Product_with_Training = product_type.objects.filter(id__in=Product).all()
    if "Product" in request.GET and request.GET["Product"]:
        Product_Ser = request.GET["Product"]
        Training_Data_ser = request.GET["Training_Data"]
        limit = request.GET["limit"]
        
        if Product_Ser == "all":
            search_data = Training_model.objects.filter(
                Training_details__contains=Training_Data_ser
            ).all()
        else:
            search_data = (
                Training_model.objects.filter(Product_name__product=Product_Ser)
                .filter(Training_details__contains=Training_Data_ser)
                .all()
            )

        paginator = Paginator(search_data, int(limit))
        page_number = request.GET.get("page")
        if page_number==None:
            page_number=1
        try:
            page_obj = paginator.get_page(
                page_number
            )  # returns the desired page object
        except PageNotAnInteger:
            # if page_number is not an integer then assign the first page
            page_obj = paginator.page(1)
            page_number = "1"
        except EmptyPage:
            # if page is empty then return last page
            page_obj = paginator.page(paginator.num_pages)
            page_number = str(paginator.num_pages)
        User_input = {
            "Training": quote(Training_Data_ser),
            "Product": Product_Ser,
            "limit": limit,
            "value":Training_Data_ser,
            "line_index_adder":((int(page_number)-1)*(int(limit))),
        }
    return render(
        request,
        "servicesupport/training.html",
        {
            "flag": 4,
            "product_type": Product_with_Training,
            "page_obj": page_obj,
            "User_input": User_input,
            
        },
    )


@login_required
def softwaretool(request):
    return render(
        request,
        "servicesupport/softwaretools.html",
        {
            "flag": 5,
        },
    )


@login_required
def softvrdy(request):
    add_analytics(request.user,"softvrdy",request)
    return render(
        request,
        "servicesupport/vrdy.html",
        {
            "flag": 5,
        },
    )


@login_required
def softwn69(request):
    add_analytics(request.user,"softwn69",request)
    return render(
        request,
        "servicesupport/wn69.html",
        {
            "flag": 5,
        },
    )


@login_required
def softnmi(request):
    add_analytics(request.user,"softnmi",request)
    return render(
        request,
        "servicesupport/nmi.html",
        {
            "flag": 5,
        },
    )

@login_required
def belttension(request):
    add_analytics(request.user,"belttension",request)
    return render(
        request,
        "servicesupport/belttension.html",
        {
            "flag": 5,
        },
    )


@login_required
def alarm(request):
    return render(
        request,
        "servicesupport/alarm.html",
        {
            "flag": 6,
        },
    )


@login_required
def alarmbynumber(request):
    add_analytics(request.user,"alarmbynumber",request)
    # empty Datasets
    page_obj = None
    search_data = alarm_detail.objects.none()
    User_input = {"system": None, "alarm": None, "limit": None}

    # product search
    Product_withALarm = alarm_detail.objects.values_list(
        "system_type", flat=True
    ).distinct()
    product_type = system_types.objects.filter(id__in=Product_withALarm).all()

    # get methods
    if "Alarm_number" in request.GET and request.GET["Alarm_number"]:
        system = request.GET["system"]
        alarm_number_ser = request.GET["Alarm_number"]
        limit = request.GET["limit"]
        if system == "all":
            search_data = alarm_detail.objects.filter(
                alarm_number__contains=alarm_number_ser
            ).all()
        else:
            search_data = (
                alarm_detail.objects.filter(system_type__system_names=system)
                .filter(alarm_number__contains=alarm_number_ser)
                .all()
            )
        User_input = {"system": system, "alarm": alarm_number_ser, "limit": limit}

        paginator = Paginator(search_data, limit)
        page_number = request.GET.get("page")
        try:
            page_obj = paginator.get_page(
                page_number
            )  # returns the desired page object
        except PageNotAnInteger:
            # if page_number is not an integer then assign the first page
            page_obj = paginator.page(1)
        except EmptyPage:
            # if page is empty then return last page
            page_obj = paginator.page(paginator.num_pages)
    return render(
        request,
        "servicesupport/alarmbynumber.html",
        {
            "flag": 6,
            "product_type": product_type,
            "User_input": User_input,
            "page_obj": page_obj,
        },
    )


@login_required
def alarmbytext(request):
    add_analytics(request.user,"alarmbytext",request)
    # empty Datasets
    page_obj = None
    search_data = alarm_detail.objects.none()
    User_input = {"system": None, "alarm": None, "limit": None}

    # product search
    Product_withALarm = alarm_detail.objects.values_list(
        "system_type", flat=True
    ).distinct()
    product_type = system_types.objects.filter(id__in=Product_withALarm).all()

    # get methods
    if "Alarm_number" in request.GET and request.GET["Alarm_number"]:
        system = request.GET["system"]
        alarm_text_ser = request.GET["Alarm_number"]
        limit = request.GET["limit"]
        if system == "all":
            search_data = alarm_detail.objects.filter(
                Q(alarm_description__contains=alarm_text_ser)
                | Q(alarm_number__contains=alarm_text_ser)
                | Q(alarm_data__contains=alarm_text_ser)
            ).all()
        else:
            search_data = (
                alarm_detail.objects.filter(system_type__system_names=system)
                .filter(
                    Q(alarm_description__contains=alarm_text_ser)
                    | Q(alarm_number__contains=alarm_text_ser)
                    | Q(alarm_data__contains=alarm_text_ser)
                )
                .all()
            )
        User_input = {"system": system, "alarm": quote(alarm_text_ser), "limit": limit, "value": alarm_text_ser}

        paginator = Paginator(search_data, limit)
        page_number = request.GET.get("page")
        try:
            page_obj = paginator.get_page(
                page_number
            )  # returns the desired page object
        except PageNotAnInteger:
            # if page_number is not an integer then assign the first page
            page_obj = paginator.page(1)
        except EmptyPage:
            # if page is empty then return last page
            page_obj = paginator.page(paginator.num_pages)
    return render(
        request,
        "servicesupport/alarmbytext.html",
        {
            "flag": 6,
            "product_type": product_type,
            "User_input": User_input,
            "page_obj": page_obj,
        },
    )


@login_required
def alarmbyled(request):
    add_analytics(request.user,"alarmbyled",request)
    Led_drive_data = led.objects.filter(
        Product_name__product_name=10
    ).all()  # 10 is id of product type
    Led_system_data = led.objects.filter(
        ~Q(Product_name__product_name=10)
    ).all()  # ~Q not starting with id == 10
    return render(
        request,
        "servicesupport/alarmbyled.html",
        {
            "flag": 6,
            "Led_drive_data": Led_drive_data,
            "Led_system_data": Led_system_data,
        },
    )


@csrf_exempt
@login_required
def spec(request):
    add_analytics(request.user,"spec",request)
    page_obj = None
    User_input = {"specno": None, "limit": None,"value":None,"line_index_adder":None,}
    photo = None
    if "specno" in request.GET and request.GET["specno"]:
        specno = request.GET["specno"]
        limit = request.GET["limit"]
        search_value = specification.objects.filter(parentspec__contains=specno).all()
        paginator = Paginator(search_value, limit)
        page_number = request.GET.get("page")
        if page_number == None:
            page_number=1
        try:
            page_obj = paginator.get_page(
                page_number
            )  # returns the desired page object
        except PageNotAnInteger:
            # if page_number is not an integer then assign the first page
            page_obj = paginator.page(1)
        except EmptyPage:
            # if page is empty then return last page
            page_obj = paginator.page(paginator.num_pages)
        photo = []
        for page in page_obj:
            if spec_details.objects.filter(spec_no=page.childspec).exists():
                photo.append(1)
            else:
                photo.append("")        
       
        User_input = {"specno": quote(specno), "limit": limit, "value":specno,"line_index_adder":((int(page_number)-1)*(int(limit))),}
    return render(
        request,
        "servicesupport/specification.html",
        {
            "flag": 7,  # active tag
            "page_obj": page_obj,
            "user_data": User_input,
            "photo":photo,
        },
    )


@login_required
def equivalent(request):
    add_analytics(request.user,"equivalent",request)
    specno = None
    search_value = equ.objects.none()  # take Spec input & search in main spec list
    search_value1 = (
        equ.objects.none()
    )  # take Spec input & search in equ spec list for any past update
    avail_parent = (
        equ.objects.none()
    )  # take spec input & search if search available in parent spc
    if request.method == "POST":
        specno = request.POST["specno"]
        search_value = equ.objects.filter(spec__contains=specno).all()

        if len(specno) > 5:
            search_value1 = equ.objects.filter(equspec__contains=specno).all()
            avail_parent = specification.objects.filter(
                childspec__contains=specno
            ).all()
        else:
            messages.info(
                request,
                "For Old Equ. Spec & Part contain in parent search via entering more than 5 char",
            )

    return render(
        request,
        "servicesupport/equ.html",
        {
            "flag": 7,  # active tag
            "serchvalue": search_value,  # sending data equ
            "serchvalue1": search_value1,  # sending data Reverse equ search
            "availparent": avail_parent,  # sending data child in parent spec
            "user_data": specno,
        },
    )


@login_required
def Spec_details(request, part_id):
    add_analytics(request.user,"Spec_details",request)
    store3 = equ.objects.none()
    store4 = equ.objects.none()
    Search_key = specification.objects.filter(id=part_id).values_list(
        "parentspec", flat=True
    )
    Main_data = specification.objects.filter(parentspec__exact=Search_key[0]).all()
    First_data = Main_data[0]

    # Search CHild spec have any future or past equivalent=nt no.
    ChildSpec = Main_data.values_list("childspec", flat=True)
    for s in ChildSpec:
        search_value3 = (
            equ.objects.filter(spec__exact=s)
            .exclude(
                reuse__exact="",
                info__exact="",
                equspec__exact="",
                srno__exact="",
                trno__exact="",
            )
            .all()
        )
        search_value4 = equ.objects.filter(
            equspec__exact=s
        ).all()  # .exclude(reuse__isnull=True).exclude(reuse__exact='').exclude(info__isnull=True).exclude(info__exact='').exclude(equspec__isnull=True).exclude(equspec__exact='').exclude(srno__isnull=True).exclude(srno__exact='').exclude(trno__isnull=True).exclude(trno__exact='').all()
        store3 = store3 | search_value3  # Child part spec equ search
        store4 = store4 | search_value4  # Child part spec reverse equ search

    return render(
        request,
        "servicesupport/specificationdetails.html",
        {
            "flag": 7,  # active tag
            "Main_data": Main_data,
            "store3": store3,
            "store4": store4,
            "First_data": First_data,
        },
    )


@login_required
def specrequest(request):
    # if not request.user.is_authenticated:
    #    messages.success(request, "Kindly Login First to access spec request")
    #    link = "/servicesupport/specification/request"
    #    return render(request, "servicesupport/login.html",{
    #        "flag": 12,
    #    })

    if request.method == "POST" and request.user.is_authenticated:
        requestadd = request.POST["option"]
        shortdetail = request.POST["shortdetail"]
        details = request.POST["details"]
        date = datetime.datetime.now()
        user = request.user
        dropdown = request.POST["dropdown"]
        data = dropdown + " | " + details
        thisdict = {
            "option": requestadd,
            "spec": shortdetail,
            "details": details,
            "dropdown": dropdown,
        }
        if len(shortdetail) >= 8 and len(details) >= 3:
            data = requesttype(
                request="Specification",
                requestadd=requestadd,
                date=date,
                user=user,
                shortdetail=shortdetail,
                details=data,
            )
            data.save()
            messages.success(request, "Your request added, Thank you for improvement")
            return HttpResponseRedirect(reverse("specification"))
        else:
            messages.error(
                request,
                "Your request not added, Please enter Spec more than 10 Char or add details",
            )
        return render(
            request,
            "servicesupport/specrequest.html",
            {
                "flag": 7,  # active tag
                "thisdict": thisdict,  # passing form
            },
        )
    else:
        return render(
            request,
            "servicesupport/specrequest.html",
            {
                "flag": 7,  # active tag
            },
        )


@login_required
def manuals(request):
    Product = manual.objects.values_list("Product_name", flat=True).distinct()
    Product_manual = system_types.objects.filter(id__in=Product)
    CNC_Product_manual = Product_manual.filter(product_name__product="CNC").all()
    ROBOT_Product_manual = (
        Product_manual.filter(id__in=Product)
        .filter(product_name__product="ROBOT")
        .all()
    )
    DRILL_Product_manual = (
        Product_manual.filter(id__in=Product)
        .filter(product_name__product="ROBODRILL")
        .all()
    )
    CUT_Product_manual = (
        Product_manual.filter(id__in=Product)
        .filter(product_name__product="ROBOCUT")
        .all()
    )
    SHOT_Product_manual = (
        Product_manual.filter(id__in=Product)
        .filter(product_name__product="ROBOSHOT")
        .all()
    )
    DRIVE_Product_manual = (
        Product_manual.filter(id__in=Product)
        .filter(product_name__product="Amplifier")
        .all()
    )

    return render(
        request,
        "servicesupport/manual.html",
        {
            "flag": 10,
            "cnc_product": CNC_Product_manual,
            "robot_product": ROBOT_Product_manual,
            "drill_product": DRILL_Product_manual,
            "cut_product": CUT_Product_manual,
            "shot_product": SHOT_Product_manual,
            "drive_product": DRIVE_Product_manual,
        },
    )


@login_required
def manualsview(request):
    add_analytics(request.user,"manualsview",request)
    if request.method == "GET":
        system = request.GET["Selection"]
        Manual_data = (
            manual.objects.filter(Product_name__system_names=system)
            .all()
            .order_by("Manual_Name")
            .all()
        )
    return render(
        request,
        "servicesupport/manualview.html",
        {
            "flag": 10,
            "manual": Manual_data,
        },
    )

@login_required
def pdf(request):
    if request.method == "GET":
        link = request.GET["link"]
        return render(
            request,
            "servicesupport/pdf.html",
            {
                "link": link,
            },
        )

@login_required
def stocks(request):
    return render(
            request,
            "servicesupport/stocks.html",
            {
                "flag": 14,
            },
        )



@login_required
@staff_member_required
def admin_data(request):
    return render(
        request,
        "servicesupport/admin_data.html",
        {
            "flag": 14,
        },
    )

@staff_member_required
def analytic_view(request):
    analytic = analytics.objects.all()
    page_list = analytic.values_list("page", flat=True).distinct().all().order_by("page")
    
    last_month = analytic.filter(updated_at__range=[(datetime.datetime.now() - datetime.timedelta(weeks=4)), datetime.datetime.now()]).all()
    last_month_Graph_data = []
    last_month_date = []
    start_date = (datetime.datetime.now() - datetime.timedelta(weeks=4)).date()
    end_date = datetime.datetime.now().date()

    # analytics 
    analytic_data = {
        "today_visit":analytic.filter(updated_at__date=end_date).count(),
        "today_visitor":analytic.filter(updated_at__date=end_date).values("user").distinct().count(),
        "all_visit":analytic.count(),
        "all_visitor":analytic.values("user").distinct().count(),
                     }
    delta = datetime.timedelta(days=1)
      
    while start_date <= end_date:
        count = last_month.filter(updated_at__date=start_date)
        last_month_date.append(str(start_date.day)+"-"+str(start_date.month))
        last_month_Graph_data.append(count.count())
        start_date += delta


    last_Month_page_count = []
    color = ["#619ED6", "#6BA547", "#F7D027", "#E48F1B", "#B77EA3", "#E64345", "#60CEED", "#9CF168", "#F7EA4A", "#FBC543", "#FFC9ED", "#E6696E"]
    i=0
    all_page_views = []
    for pages in page_list:
            count = analytic.filter(page=pages).count()
            all_page_views.append({'page':count,'color':color[i],'page_name':pages})
            i+=1
    
    i=0
    for pages in page_list:
        start_date = (datetime.datetime.now() - datetime.timedelta(weeks=4)).date()
        end_date = datetime.datetime.now().date()
        delta = datetime.timedelta(days=1)
        page_count = []
        while start_date <= end_date:
            count = last_month.filter(updated_at__date=start_date).filter(page=pages)
            page_count.append(count.count()) 
            start_date += delta  
        last_Month_page_count.append({'page':page_count,'color':color[i],'page_name':pages})
        i+=1        
        
    return render(
        request,
        "servicesupport/analytic_view.html",
        {
            "flag": 14,
            "page_list":page_list,
            "last_month_date":last_month_date,
            "last_month_Graph_data":last_month_Graph_data,
            "mixed_page_vise_last_month": last_Month_page_count,
            "all_page_views":all_page_views,
            "analytic_data":analytic_data,
        },
    )


@staff_member_required
def analytic_report(request):
    User_data = {"user_selected":None,"from_date":None, "to_date":None}
    page_list = analytics.objects.values_list("page", flat=True).distinct().all().order_by("page")
    person_list = analytics.objects.values("user").distinct()
    views_result = None
    data_result_page = None
    all_page_views = None
    Visits = None
    Visitors = None
    if request.method == "POST":
        user_details = request.POST["user_selected"]
        from_date = request.POST["from_date"]
        to_date = request.POST["to_date"]
        User_data= {"user_selected":user_details,"from_date":from_date, "to_date":to_date}
        if user_details == "all":
            data = analytics.objects.filter(updated_at__range=[from_date, to_date]).all()
        else:
            data = analytics.objects.filter(user=user_details).filter(updated_at__range=[from_date, to_date]).all() 

        Visits = data.count()
        Visitors = data.values("user").distinct().count()   

        color = ["#619ED6", "#6BA547", "#F7D027", "#E48F1B", "#B77EA3", "#E64345", "#60CEED", "#9CF168", "#F7EA4A", "#FBC543", "#FFC9ED", "#E6696E"]

        i=0
        all_page_views = []
        for pages in page_list:
                count = data.filter(page=pages).count()
                all_page_views.append({'page':count,'color':color[i],'page_name':pages})
                i+=1
        i=0
        data_result_page =[]
        for pages in page_list:
            start_date = (datetime.datetime.fromisoformat(from_date).date())
            end_date = (datetime.datetime.fromisoformat(to_date).date())
            delta = datetime.timedelta(days=1)
            page_count = []
            while start_date <= end_date:
                count = data.filter(updated_at__date=start_date).filter(page=pages)
                page_count.append(count.count()) 
                start_date += delta  
            data_result_page.append({'page':page_count,'color':color[i],'page_name':pages})
            i+=1

        start_date = (datetime.datetime.fromisoformat(from_date).date())
        end_date = (datetime.datetime.fromisoformat(to_date).date())
        views_result= []
        while start_date <= end_date:
            count = data.filter(updated_at__date=start_date)
            views_result.append({'date':str(start_date.day)+"-"+str(start_date.month),'count':count.count()})
            start_date += delta  

    return render(
        request,
        "servicesupport/analytic_report.html",
        {
            "flag": 14,
            "page_list":page_list,
            "views_result":views_result,
            "data_result_page":data_result_page,
            "all_page_views": all_page_views,
            "Visits":Visits,
            "Visitors":Visitors,
            "User_data":User_data,
            "person_list":person_list,
        },
    )

@staff_member_required
def csv_output(request):
    if request.method == "POST":
        user_details = request.POST["user_selected"]
        from_date = request.POST["from_date"]
        to_date = request.POST["to_date"]
        User_data= {"user_selected":user_details,"from_date":from_date, "to_date":to_date}
        if user_details == "all":
            data = analytics.objects.filter(updated_at__range=[from_date, to_date]).all()
        else:
            data = analytics.objects.filter(user=user_details).filter(updated_at__range=[from_date, to_date]).all()
        response = HttpResponse(content_type='text/csv')  
        response['Content-Disposition'] = 'attachment; filename="file.csv"'  
        
        writer = csv.writer(response)  
        writer.writerow(["User Name","Page Name","Visited at","IP Address"])
        for value in data:  
            writer.writerow([value.user,value.page,value.updated_at,value.ip])  
        return response       

def repair_list(request):
    pass

def checklist(request,list_id):
    pass
    
@csrf_exempt
@login_required
def photo(request, spec):

    # Query for requested email
    try:
        data = spec_details.objects.filter(spec_no=spec).all()
    except spec_details.DoesNotExist:
        return JsonResponse({"error": "Photo not found."}, status=404)

    # Return email contents
    #if request.method == "GET":
    return JsonResponse([email.serialize() for email in data], safe=False) 
    #else:
    #    return JsonResponse({
    #        "error": "GET request required."
    #   }, status=400)   


def Stock_update(request):
    if request.method == "POST":
        pass



@csrf_exempt
def receive_stock_data(request):
    if request.method == 'POST':
            item = json.loads(request.body)
            
            Stock.objects.all().delete()
            # Extract relevant fields from JSON data
            for data in item:
                
                    material_id = data.get('Material')
                    if material_id is not None:    
                        plant_id = data.get('Plant')
                        storage_id = data.get('Storage Location')
                        special_stock = data.get('Special Stock')
                        special_stock_number = data.get('Special stock number')
                        available = data.get('Unrestricted')
                        transit = data.get('Transit and Transfer')
                        returns = data.get('Returns')
                        
                        # Check if the material exists in spec_details
                        material_instance, created = spec_details.objects.get_or_create(spec_no=material_id)
                        plant_instance = Plant.objects.get(code=plant_id)
                        
                        storage_instance = None
                        if storage_id is not None:
                            storage_instance = Storage_loc.objects.get(storage_location=storage_id)

                        # Create or update Stock instance
                        stock_instance = Stock.objects.create(
                                material=material_instance,
                                plant=plant_instance,
                                storage=storage_instance,
                                special_stock=special_stock,
                                special_stock_number=special_stock_number,
                                available=available,
                                transit=transit,
                                returns=returns,
                                
                            )
            
            return JsonResponse({'message': 'Data saved successfully.'})
        
        #except Exception as e:
        #    return JsonResponse({'error': str(e)}, status=400)
    
    else:
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)

import pandas as pd

@csrf_exempt
def receive_stock_data2(request):
    if request.method == 'POST':
        #try:
            items = json.loads(request.body)
            
            # Convert JSON data to pandas DataFrame
            df = pd.DataFrame(items)
            
            # Delete all existing Stock objects
            Stock.objects.all().delete()
            
            # Fetch existing data for material from spec_details table
            spec_details_data = spec_details.objects.all().values_list('spec_no', 'id')
            spec_details_df = pd.DataFrame(spec_details_data, columns=['spec_no', 'id'])
            
            # Merge DataFrame with spec_details data to map spec_no to material_id
            df = df.merge(spec_details_df, how='left', left_on='Material', right_on='spec_no')
            df.drop(columns=['spec_no'], inplace=True)
            df.rename(columns={'id': 'material'}, inplace=True)
            
            # Create new materials for missing spec_no
            missing_materials = df[df['material'].isnull()]['Material'].unique()
            for material in missing_materials:
                new_material = spec_details.objects.create(spec_no=material)
                df.loc[df['Material'] == material, 'material'] = new_material.id
            
            # Fetch existing data for plant from Plant table
            plant_data = Plant.objects.all().values_list('code', 'id')
            plant_df = pd.DataFrame(plant_data, columns=['code', 'id'])
            
            # Merge DataFrame with Plant data to map code to plant_id
            df = df.merge(plant_df, how='left', left_on='Plant', right_on='code')
            df.drop(columns=['code'], inplace=True)
            df.rename(columns={'id': 'plant'}, inplace=True)
            
            # Handle empty storage locations
            df['storage'] = df['Storage Location'].apply(lambda x: Storage_loc.objects.get(storage_location=x).id if pd.notnull(x) else None)
            
            # Drop the 'Storage Location' column
            df.drop(columns=['Storage Location'], inplace=True)
            
            # Create Stock objects from DataFrame
            Stock.objects.bulk_create(
                Stock(
                    material_id=row['material'],
                    plant_id=row['plant'],
                    storage_id=row['storage'],
                    special_stock=row['Special Stock'],
                    special_stock_number=row['Special stock number'],
                    batch=row['Batch'],
                    available=row['Unrestricted'],
                    transit=row['Transit and Transfer'],
                    returns=row['Returns']
                )
                for _, row in df.iterrows()
            )
            
            return JsonResponse({'message': 'Data saved successfully.'})
        
        #except Exception as e:
        #    return JsonResponse({'error': str(e)}, status=400)
    
    else:
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)
# Create your views here.
@login_required
def serial_gen(request):
    serial_no = Serial_Number.objects.order_by('updated_at').first()

    if request.method == "POST":
        SerialNumber = request.POST["serial_no"]
        add_text_data = request.POST["add_text"]
        data = Serial_Number(
                serial_no=SerialNumber,
                add_text=add_text_data,
                user=request.user,
            )
        data.save()

    return render(
        request,
        "servicesupport/serial_number.html",
        {
            "serial_no": serial_no,
        }
    )

def get_latest_serial_number(request):
    # Fetch the latest serial number from the database
    if Serial_Number.objects.count()==0:
        data = Serial_Number(
                serial_no="0",
                add_text="",
                user=request.user,
            )
        data.save()
        
    latest_serial_number = Serial_Number.objects.latest('updated_at')
    
    
        
    # Convert the serial number to hexadecimal
    latest_serial_hex = hex(int(latest_serial_number.serial_no, 16) + 1)
    
    # Return the serial number as JSON response
    return JsonResponse({'serial_no': latest_serial_hex})

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import *
from .serializers import *
from django.db.models import Q

# Create your views here.

@permission_classes((AllowAny, ))
class Alarm_search(APIView, LimitOffsetPagination):
    def get(self, request,*args, **kwargs):

        # if Query Params
        search_para = self.request.query_params.get("alarm",None)
        search_system = self.request.query_params.get("system",None)

        if search_para and search_system: # alarm filter
            queryset = alarm_detail.objects.filter(system_type__system_names=search_system).filter(
                Q(alarm_description__contains=search_para)
                | Q(alarm_number__contains=search_para)
                | Q(alarm_data__contains=search_para)
            )
        elif search_system:
            queryset = alarm_detail.objects.filter(system_type__system_names=search_system)    
        elif search_para:
            queryset = alarm_detail.objects.filter(
                Q(alarm_description__contains=search_para)
                | Q(alarm_number__contains=search_para)
                | Q(alarm_data__contains=search_para)
            )
        else:
            queryset = alarm_detail.objects.all()   

         
        results = self.paginate_queryset(queryset, request, view=self)
        serializer = CustomAlarmSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

@permission_classes((AllowAny, ))
class Systems(APIView):
    def get(self, request,*args, **kwargs):
        search_para = self.request.query_params.get("view",None)
        if search_para:
            if search_para == "alarm":
                Product_withALarm = alarm_detail.objects.values_list("system_type", flat=True).distinct()
                queryset = system_types.objects.filter(id__in=Product_withALarm).all()
            elif search_para == "manual":
                Product_withManual = manual.objects.values_list("Product_name",flat=True).distinct()
                queryset = system_types.objects.filter(id__in=Product_withManual).all()
        else:    
            queryset = system_types.objects.all()
        serializers = CustomSystemsSerializer(queryset,many=True)
        return Response(serializers.data)

@permission_classes((AllowAny, ))
class Training_search(APIView, LimitOffsetPagination):
    def get(self, request,*args, **kwargs):
        
        search_para = self.request.query_params.get("training",None)

        if search_para:
            queryset = Training_model.objects.filter(
                Q(Training_Name__contains=search_para)
                | Q(Training_details__contains=search_para)
            )
        else:
            queryset = Training_model.objects.all()

        results = self.paginate_queryset(queryset, request, view=self)
        serializer = CustomTrainingSerializer(results, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

@permission_classes((AllowAny, ))
class Parent_spec(APIView, LimitOffsetPagination):
    def get(self, request, *args, **kwargs):
        search_para = self.request.query_params.get("spec",None)
        if search_para:
            queryset = specification.objects.filter(parentspec__contains=search_para)
        else:
            queryset = specification.objects.all()    

        results = self.paginate_queryset(queryset,request, view=self)
        serializers = CustomParent_specSerializer(results, many=True)
        return self.get_paginated_response(serializers.data)  

@permission_classes((AllowAny, ))
class Child_spec(APIView, LimitOffsetPagination):
    def get(self, request, *args, **kwargs):
        search_para = self.request.query_params.get("spec",None)
        search_para_flag= self.request.query_params.get("flag",None)
        if search_para and search_para_flag:
            if search_para_flag=="new":
                queryset= equ.objects.filter(spec__contains=search_para)
            elif search_para_flag=="old":
                queryset= equ.objects.filter(equspec__contains=search_para)    
        elif search_para:
            queryset= equ.objects.filter(spec__contains=search_para) |equ.objects.filter(equspec__contains=search_para)
        else:    
            queryset = equ.objects.all()

        results = self.paginate_queryset(queryset,request, view=self)
        serializers = CustomChild_specSerializer(results, many=True)
        return self.get_paginated_response(serializers.data)  

@permission_classes((AllowAny, ))
class Parent_child(APIView):
    def get(self,request,part_id, *args, **kwargs):
        parent_spec = specification.objects.filter(id=part_id).first()
        if not parent_spec:
            # Handle the case when the parent specification with the given ID is not found
            return Response({"error": "Parent specification not found"}, status=404)
        filter_q= specification.objects.filter(id=part_id).values_list("parentspec", flat=True)
        
        queryset = specification.objects.filter(parentspec__exact=filter_q[0]).all()

        ChildSpec = queryset.values_list("childspec", flat=True)
        queryset2 = equ.objects.none()
        queryset3 = equ.objects.none()
        for s in ChildSpec:
            queryset2 =  queryset2 | equ.objects.filter(spec__exact=s).exclude(
                reuse__exact="",
                info__exact="",
                equspec__exact="",
                srno__exact="",
                trno__exact="",
            ).all()   # New Equ parts search
            queryset3 = queryset3 | equ.objects.filter(equspec__exact=s).all() # Old Equ parts Search
        
        serializers = CustomParent_childSerializer(queryset,many=True) # Parent parts child specs
        serializers1 = CustomChild_specSerializer(queryset2,many=True) # New equ Serializer 
        serializers2 = CustomChild_specSerializer(queryset3,many=True) # Old Equ Serializer

        response_data = {
            'queryset1': serializers.data,
            'queryset2': serializers1.data,
            'queryset3': serializers2.data
        }

        return Response(response_data)

@permission_classes((AllowAny, ))
class Parent_available(APIView):     
    def get(self,request, *args, **kwargs):
        search_para = self.request.query_params.get("spec",None)

        if search_para:
            queryset = specification.objects.filter(childspec__exact=search_para).all()
        else:
            return Response({"error": "Parent specification not found"}, status=404)
        
        serializers = CustomParent_childSerializer(queryset,many=True) # Parent parts child specs
        return Response(serializers.data)

@permission_classes((AllowAny, ))
class Manual(APIView, LimitOffsetPagination):
    def get(self, request,*args, **kwargs):
        
        search_para = self.request.query_params.get("manual",None)
        search_product = self.request.query_params.get("product",None)

        if search_para and search_product:
            queryset = manual.objects.filter(Manual_Name__contains=search_para).filter(system_type__system_names=search_product)
        elif search_product:
            queryset = manual.objects.filter(system_type__system_names=search_product)
        elif search_para:
            queryset = manual.objects.filter(Manual_Name__contains=search_para)
        else:
            queryset = manual.objects.all()

        results = self.paginate_queryset(queryset, request, view=self)
        serializer = CustomManualSerializer(results, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)
    

class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = CustomStocksSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['spec', 'description']  # General search fields

    def get_queryset(self):
        queryset = super().get_queryset()
        request = self.request
        search_spec = request.query_params.get('columns[0][search][value]', None)
        search_name = request.query_params.get('columns[1][search][value]', None)
        
        search_plant = request.query_params.get('columns[2][search][value]', None)
        search_storage_location = request.query_params.get('columns[3][search][value]', None)
        print(search_spec)
        print(search_name)
        print(search_plant)
        print(search_storage_location)
        if search_spec:
            queryset = queryset.filter(material__spec_no__icontains=search_spec)
        if search_name:
            queryset = queryset.filter(material__description__icontains=search_spec)
        if search_plant:
            queryset = queryset.filter(plant__name__icontains=search_plant)
        if search_storage_location:
            queryset = queryset.filter(storage__storage_location__icontains=search_storage_location)

        # Handle global search
        search_value = request.query_params.get('search[value]', None)
        if search_value:
            queryset = queryset.filter(
                Q(material__spec_no__icontains=search_value) |
                Q(material__description__icontains=search_value) |
                Q(plant__name__icontains=search_value)
            )

         # Handle sorting
        order_column_index = request.query_params.get('order[0][column]', None)
        order_dir = request.query_params.get('order[0][dir]', 'asc')
        if order_column_index is not None:
            columns = ['material', 'material_name', 'plant',"storage","special_stock","special_stock_number","available","transit","returns"]
            order_column = columns[int(order_column_index)]
            if order_dir == 'desc':
                order_column = '-' + order_column
            queryset = queryset.order_by(order_column)

        return queryset    

 
# ── HELPER ────────────────────────────────────────────────────
 
def is_reviewer(user):
    """True if user belongs to Reviewer/Manager/ST_Reviewer group, or is superuser."""
    return user.is_superuser or user.groups.filter(
        name__in=["Reviewer", "Manager", "ST_Reviewer"]
    ).exists()
 
 
# ── 1. LIST ───────────────────────────────────────────────────
 
@login_required
def std_list(request):
    q       = request.GET.get("q", "").strip()
    product = request.GET.get("product", "")
    status  = request.GET.get("status", "")
 
    if is_reviewer(request.user):
        reports = STDReport.objects.select_related("prepared_by", "reviewed_by")
    else:
        reports = STDReport.objects.filter(
            Q(prepared_by=request.user) | Q(status="published")
        ).select_related("prepared_by")
 
    if q:
        reports = reports.filter(
            Q(subject__icontains=q)          |
            Q(end_user__icontains=q)         |
            Q(controller_model__icontains=q) |
            Q(mr_no__icontains=q)
        )
    if product:
        reports = reports.filter(product=product)
    if status:
        reports = reports.filter(status=status)
 
    page_obj = Paginator(reports, 15).get_page(request.GET.get("page", 1))
    add_analytics(request.user, "std", request)
 
    return render(request, "servicesupport/std_list.html", {
        "flag":            3,
        "page_obj":        page_obj,
        "q":               q,
        "product":         product,
        "status":          status,
        "is_reviewer":     is_reviewer(request.user),
        "product_choices": STDReport._meta.get_field("product").choices,
        "status_choices":  STDReport._meta.get_field("status").choices,
    })
 
 
# ── 2. CREATE / EDIT ──────────────────────────────────────────
 
@login_required
def std_form(request, report_id=None):
    report = None
    if report_id:
        report = get_object_or_404(STDReport, id=report_id)
        if report.prepared_by != request.user and not is_reviewer(request.user):
            messages.error(request, "You don't have permission to edit this report.")
            return HttpResponseRedirect(reverse("std"))
        if report.status in ("approved", "published") and not is_reviewer(request.user):
            messages.error(request, "Approved report — contact a reviewer to edit.")
            return HttpResponseRedirect(reverse("std_detail", args=[report_id]))
 
    if request.method == "POST":
        action = request.POST.get("action", "save_draft")
 
        # Parse dynamic parts rows
        specs   = request.POST.getlist("part_spec[]")
        qtys    = request.POST.getlist("part_qty[]")
        reasons = request.POST.getlist("part_reason[]")
        parts   = [
            {"spec": s.strip(), "qty": q.strip(), "reason": r.strip()}
            for s, q, r in zip(specs, qtys, reasons)
            if s.strip()
        ]
 
        fields = {
            "subject":              request.POST.get("subject", "").strip(),
            "product":              request.POST.get("product", ""),
            "content_type":         request.POST.get("content_type", "Content/Solution"),
            "controller_model":     request.POST.get("controller_model", ""),
            "controller_sl_no":     request.POST.get("controller_sl_no", ""),
            "machine_model":        request.POST.get("machine_model", ""),
            "machine_sl_no":        request.POST.get("machine_sl_no", ""),
            "rm_model":             request.POST.get("rm_model", ""),
            "rm_sl_no":             request.POST.get("rm_sl_no", ""),
            "machine_tool_builder": request.POST.get("machine_tool_builder", ""),
            "configuration":        request.POST.get("configuration", ""),
            "end_user":             request.POST.get("end_user", ""),
            "application":          request.POST.get("application", ""),
            "mr_no":                request.POST.get("mr_no", ""),
            "is_multiple_visit":    request.POST.get("is_multiple_visit") == "on",
            "visits_count":         int(request.POST.get("visits_count") or 1),
            "hours_count":          int(request.POST.get("hours_count") or 0),
            "repeat_visit_reason":  request.POST.get("repeat_visit_reason", ""),
            "reason_for_subject":   request.POST.get("reason_for_subject", ""),
            "problem_reported":     request.POST.get("problem_reported", ""),
            "problem_observation":  request.POST.get("problem_observation", ""),
            "problem_suspected":    request.POST.get("problem_suspected", ""),
            "problem_history":      request.POST.get("problem_history", ""),
            "external_disturbance": request.POST.get("external_disturbance", ""),
            "occurrence_count":     request.POST.get("occurrence_count", ""),
            "diagnosis_info":       request.POST.get("diagnosis_info", ""),
            # CKEditor submits content via hidden textarea — these are the HTML strings
            "analysis":             request.POST.get("analysis", ""),
            "solution":             request.POST.get("solution", ""),
            "additional_info":      request.POST.get("additional_info", ""),
            "parts_used_json":      json.dumps(parts),
        }
 
        if not fields["subject"]:
            messages.error(request, "Subject is required.")
            return render(request, "servicesupport/std_form.html", {
                "flag":            3,
                "report":          report,
                "product_choices": STDReport._meta.get_field("product").choices,
                "content_choices": STDReport._meta.get_field("content_type").choices,
                "system_types":    system_types.objects.all(),
            })
 
        if report is None:
            report = STDReport(prepared_by=request.user)
 
        for k, v in fields.items():
            setattr(report, k, v)
 
        if action == "submit":
            report.status       = "submitted"
            report.submitted_at = timezone.now()
        else:
            # Don't downgrade if already approved/published (reviewer editing)
            if report.status not in ("approved", "published", "submitted"):
                report.status = "draft"
 
        report.save()
 
        STDApprovalLog.objects.create(
            report=report,
            action=action,
            actor=request.user,
            comment="Submitted for review" if action == "submit" else "Saved draft",
        )
 
        if action == "submit":
            messages.success(request, f"'{report.subject[:40]}' submitted for review.")
        else:
            messages.success(request, "Draft saved.")
 
        return HttpResponseRedirect(reverse("std_detail", args=[report.id]))
 
    return render(request, "servicesupport/std_form.html", {
        "flag":            3,
        "report":          report,
        "product_choices": STDReport._meta.get_field("product").choices,
        "content_choices": STDReport._meta.get_field("content_type").choices,
        "system_types":    system_types.objects.all().select_related("product_name"),
    })
 
 
# ── 3. DETAIL ─────────────────────────────────────────────────
 
@login_required
def std_detail(request, report_id):
    report = get_object_or_404(STDReport, id=report_id)
 
    # Access control — drafts/rejected only visible to author + reviewers
    if report.status not in ("published", "approved", "submitted"):
        if report.prepared_by != request.user and not is_reviewer(request.user):
            messages.error(request, "This report is not yet published.")
            return HttpResponseRedirect(reverse("std"))
 
    log = report.approval_log.select_related("actor").all()
    add_analytics(request.user, "std", request)
 
    # Reviewer can access review panel from submitted OR approved state
    can_review = is_reviewer(request.user) and report.status in ("submitted", "approved")
 
    return render(request, "servicesupport/std_detail.html", {
        "flag":        3,
        "report":      report,
        "log":         log,
        "is_reviewer": is_reviewer(request.user),
        "can_review":  can_review,
        "can_edit": (
            report.prepared_by == request.user and
            report.status in ("draft", "rejected")
        ) or is_reviewer(request.user),
    })
 
 
# ── 4. REVIEW / APPROVE / PUBLISH ────────────────────────────
 
@login_required
def std_review(request, report_id):
    if not is_reviewer(request.user):
        messages.error(request, "You don't have reviewer access.")
        return HttpResponseRedirect(reverse("std"))
 
    report = get_object_or_404(STDReport, id=report_id)
 
    # Allow access from submitted AND approved (so reviewer can still publish after approve)
    if report.status not in ("submitted", "approved"):
        messages.error(request, f"Cannot review a report with status '{report.get_status_display()}'.")
        return HttpResponseRedirect(reverse("std_detail", args=[report_id]))
 
    if request.method == "POST":
        action  = request.POST.get("action", "").strip()
        comment = request.POST.get("comment", "").strip()
 
        # Always save reviewer fields regardless of action
        report.applicable_models = request.POST.get("applicable_models", "")
        report.useful_telephonic = request.POST.get("useful_telephonic") == "yes"
        report.supports_mttr     = request.POST.get("supports_mttr") == "yes"
        report.special_tool      = request.POST.get("special_tool", "")
        report.alternate_process = request.POST.get("alternate_process", "")
        report.reviewer_remarks  = request.POST.get("reviewer_remarks", "")
        report.reviewed_by       = request.user
 
        # ── Status transition ──────────────────────────────────
        if action == "approve":
            report.status      = "approved"
            report.approved_at = timezone.now()
            msg = "Report approved. Use 'Approve & Publish' to make it visible to all engineers."
 
        elif action == "publish":
            report.status      = "published"                          # ← KEY FIX
            report.approved_at = report.approved_at or timezone.now() # set if not already set
            msg = "Report published — now visible to all engineers."
 
        elif action == "reject":
            report.status = "rejected"
            msg = "Report sent back to author for revision."
 
        else:
            messages.error(request, f"Unknown action: '{action}'")
            return HttpResponseRedirect(reverse("std_review", args=[report_id]))
 
        # ── Save FIRST, then log ───────────────────────────────
        report.save()
 
        STDApprovalLog.objects.create(
            report=report,
            action=action,
            actor=request.user,
            comment=comment or msg,
        )
 
        messages.success(request, msg)
        return HttpResponseRedirect(reverse("std_detail", args=[report.id]))
 
    # GET — show review form
    log = report.approval_log.select_related("actor").all()
    return render(request, "servicesupport/std_review.html", {
        "flag":   3,
        "report": report,
        "log":    log,
    })



# ── Helpers ───────────────────────────────────────────────────
 
def _session_key(request):
    """Unique session key per user so parallel uploads don't clash."""
    return f'std_import_{request.user.pk}'
 
 
def _cleanup_img_dir(img_dir):
    """Delete imported images folder if it exists."""
    if img_dir and os.path.isdir(img_dir):
        try:
            shutil.rmtree(img_dir)
        except Exception:
            pass
 
 
# ── View 1: Upload page ───────────────────────────────────────
 
@login_required
def std_import(request):
    """GET — show the upload page."""
    return render(request, 'servicesupport/std_import.html', {'flag': 3})
 
 
# ── View 2: Parse + Preview + Save ───────────────────────────
 
@login_required
def std_import_preview(request):
    """
    POST  → parse the uploaded .docx, store field data in session
             (images are on disk as /media/std_imports/<uuid>/...),
             then show the editable preview page.
 
    GET ?save=1 → read session data, create STDReport draft,
                  redirect to edit page.
    """
 
    # ── POST: parse file ──────────────────────────────────────
    if request.method == 'POST':
        uploaded = request.FILES.get('docx_file')
        if not uploaded:
            messages.error(request, 'Please select a .docx file.')
            return HttpResponseRedirect(reverse('std_import'))
 
        if not uploaded.name.lower().endswith('.docx'):
            messages.error(request, 'Only .docx files are supported.')
            return HttpResponseRedirect(reverse('std_import'))
 
        if uploaded.size > 30 * 1024 * 1024:
            messages.error(request, 'File is too large (max 30 MB).')
            return HttpResponseRedirect(reverse('std_import'))
 
        # Clean up any previous incomplete import for this user
        skey = _session_key(request)
        prev = request.session.get(skey)
        if prev:
            _cleanup_img_dir(prev.get('_img_dir'))
 
        try:
            data = parse_std_docx(uploaded, media_root=settings.MEDIA_ROOT)
        except Exception as e:
            messages.error(request, f'Could not read the file: {e}')
            return HttpResponseRedirect(reverse('std_import'))
 
        # Store in session — analysis/solution contain only small URL strings now
        session_data = {k: v for k, v in data.items() if not k.startswith('_') or k == '_img_dir'}
        session_data['_img_dir']   = data.get('_img_dir', '')
        session_data['_filename']  = uploaded.name
        request.session[skey]      = session_data
        request.session.modified   = True
 
        # Build parts_list for template display
        try:
            parts_list = json.loads(data.get('parts_used_json', '[]'))
        except Exception:
            parts_list = []
 
        return render(request, 'servicesupport/std_import_preview.html', {
            'flag':            3,
            'data':            data,
            'parts_list':      parts_list,
            'filename':        uploaded.name,
            'product_choices': STDReport._meta.get_field('product').choices,
            'content_choices': STDReport._meta.get_field('content_type').choices,
        })
 
    # ── GET ?save=1: write draft to database ──────────────────
    if request.GET.get('save') == '1':
        skey = _session_key(request)
        data = request.session.get(skey)
 
        if not data:
            messages.error(request, 'Session expired. Please upload the file again.')
            return HttpResponseRedirect(reverse('std_import'))
 
        try:
            # Allow engineer to override any field from the preview form GET params
            overridable = (
                'subject', 'product', 'content_type',
                'controller_model', 'controller_sl_no',
                'rm_model', 'rm_sl_no',
                'machine_model', 'machine_sl_no',
                'machine_tool_builder', 'configuration',
                'end_user', 'application', 'mr_no',
                'visits_count', 'hours_count',
                'repeat_visit_reason', 'reason_for_subject',
                'problem_reported', 'problem_observation',
                'problem_suspected', 'problem_history',
                'external_disturbance', 'occurrence_count',
                'diagnosis_info', 'analysis', 'solution',
                'additional_info', 'parts_used_json',
            )
            for field in overridable:
                if field in request.GET and request.GET[field].strip():
                    data[field] = request.GET[field]
 
            report = STDReport(
                prepared_by          = request.user,
                status               = 'draft',
                subject              = data.get('subject', ''),
                product              = data.get('product', ''),
                content_type         = data.get('content_type', 'Content/Solution'),
                controller_model     = data.get('controller_model', ''),
                controller_sl_no     = data.get('controller_sl_no', ''),
                rm_model             = data.get('rm_model', ''),
                rm_sl_no             = data.get('rm_sl_no', ''),
                machine_model        = data.get('machine_model', ''),
                machine_sl_no        = data.get('machine_sl_no', ''),
                machine_tool_builder = data.get('machine_tool_builder', ''),
                configuration        = data.get('configuration', ''),
                end_user             = data.get('end_user', ''),
                application          = data.get('application', ''),
                mr_no                = data.get('mr_no', ''),
                visits_count         = int(data.get('visits_count') or 1),
                hours_count          = int(data.get('hours_count') or 0),
                repeat_visit_reason  = data.get('repeat_visit_reason', ''),
                reason_for_subject   = data.get('reason_for_subject', ''),
                problem_reported     = data.get('problem_reported', ''),
                problem_observation  = data.get('problem_observation', ''),
                problem_suspected    = data.get('problem_suspected', ''),
                problem_history      = data.get('problem_history', ''),
                external_disturbance = data.get('external_disturbance', ''),
                occurrence_count     = data.get('occurrence_count', ''),
                diagnosis_info       = data.get('diagnosis_info', ''),
                analysis             = data.get('analysis', ''),
                solution             = data.get('solution', ''),
                additional_info      = data.get('additional_info', ''),
                parts_used_json      = data.get('parts_used_json', '[]'),
            )
            report.save()
 
            STDApprovalLog.objects.create(
                report  = report,
                action  = 'imported',
                actor   = request.user,
                comment = f"Imported from Word: {data.get('_filename', '?')}",
            )
 
            # Clear session
            del request.session[skey]
            request.session.modified = True
 
            messages.success(
                request,
                f"Draft saved as STD-{report.created_at.year}-{report.id:04d}. "
                f"Review the content and submit when ready."
            )
            return HttpResponseRedirect(reverse('std_edit', args=[report.id]))
 
        except Exception as e:
            # Don't clean up images — user may retry
            messages.error(request, f'Error saving draft: {e}')
            return HttpResponseRedirect(reverse('std_import'))
 
    return HttpResponseRedirect(reverse('std_import'))