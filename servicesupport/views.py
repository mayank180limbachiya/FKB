from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.admin.views.decorators import staff_member_required
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
    analytics
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
                "servicesupport/Index.html",
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
            print("Email Available")
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
            print("not available")    
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
        "servicesupport/Index.html",
        {
            "flag": 13,
        },
    )


def index(request):
    return render(
        request,
        "servicesupport/Index.html",
        {
            "flag": 1,
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
        print(page_number)
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


@login_required
def spec(request):
    add_analytics(request.user,"spec",request)
    page_obj = None
    User_input = {"specno": None, "limit": None,"value":None,"line_index_adder":None,}

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
        User_input = {"specno": quote(specno), "limit": limit, "value":specno,"line_index_adder":((int(page_number)-1)*(int(limit))),}
    return render(
        request,
        "servicesupport/specification.html",
        {
            "flag": 7,  # active tag
            "page_obj": page_obj,
            "user_data": User_input,
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
    print(First_data.parentspec, First_data.parentname)

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


# Create your views here.
