<<<<<<< HEAD
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core import serializers
from django.db.models import Count
import json

#from tablib import Dataset #for data read
from django.db.models import Q
import datetime

import servicesupport
from .models import  alarm_detail, alarm_report, equ, product_type, specification, system_types, userdetails ,requesttype ,manual, Training_model


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            messages.success(request, 'login Success')
            login(request, user)
            return render(request, "servicesupport/Index.html",{
            "flag": 1,
            })  
        else:
            messages.error(request, 'wrong User ID or password - for support contact Admin')
            return render(request, "servicesupport/login.html",{
            "flag": 12,
            })
    else:
        return render(request, "servicesupport/login.html",{
            "flag": 12,
        })    

def register(request):
    return render(request, "servicesupport/Index.html",{
        "flag": 2,
    })
          

def logout_view(request):
    logout(request)
    messages.success(request, 'logout Success')
    return render(request, "servicesupport/Index.html",{
        "flag": 13,
    }) 
    
def index(request):
    return render(request, "servicesupport/Index.html",{
        "flag": 1,
    })

def std(request):
    return render(request, "servicesupport/std.html",{
        "flag": 3,
    })

def training(request):
    Training_Data_ser = None
    Product_Ser =None
    search_data = Training_model.objects.none()
    Product = Training_model.objects.values_list('Product_name',flat=True).distinct()
    Product_with_Training = product_type.objects.filter(id__in=Product).all()
    if request.method == 'POST':
        Product_Ser = request.POST["Product"]
        Training_Data_ser = request.POST["Training_Data"]
        if len(Training_Data_ser) >= 0:
            if Product_Ser =="all": 
                search_data = Training_model.objects.filter( Training_details__icontains=Training_Data_ser).all()
            else:
                search_data = Training_model.objects.filter(Product_name__product = Product_Ser).filter( Training_details__icontains = Training_Data_ser).all()

    return render(request, "servicesupport/training.html",{
        "flag": 4,
        "product_type":Product_with_Training,
        "Training_Data_ser":Training_Data_ser,
        "Product_Ser":Product_Ser,
        "search_data":search_data,
    })

def softwaretool(request):
    return render(request, "servicesupport/softwaretools.html",{
        "flag": 5,
    })

def softvrdy(request):
    return render(request, "servicesupport/vrdy.html",{
        "flag": 5,
    })

def softwn69(request):
    return render(request, "servicesupport/wn69.html",{
        "flag": 5,
    })

def softnmi(request):
    return render(request, "servicesupport/nmi.html",{
        "flag": 5,
    })

def alarm(request):
    return render(request, "servicesupport/alarm.html",{
        "flag": 6,
    })   

def alarmbynumber(request):
    system = None
    alarm_number_ser = None
    #product_type = system_types.objects.all()
    Product_withALarm = alarm_detail.objects.values_list('system_type',flat=True).distinct()
    product_type = system_types.objects.filter(id__in=Product_withALarm).all()

    search_data = alarm_detail.objects.none()
    if request.method == 'POST':
        system = request.POST["system"]
        alarm_number_ser = request.POST["Alarm_number"]
        print(system,alarm_number_ser)
        if len(alarm_number_ser) > 0:
            if system =="all": 
                search_data = alarm_detail.objects.filter( alarm_number__icontains=alarm_number_ser).all() 
            else:
                search_data = alarm_detail.objects.filter(system_type__system_names = system).filter( alarm_number__icontains = alarm_number_ser).all() 
        else:
            messages.error(request, "Kindly Search via entering more than 1 char")
    return render(request, "servicesupport/alarmbynumber.html",{
        "flag": 6,
        "product_type":product_type,
        "search_data":search_data,
        "system":system,
        "alarm_number_ser":alarm_number_ser,
    }) 

def alarmbytext(request):
    system = None
    alarm_text_ser = None
    product_type = system_types.objects.all()
    search_data = alarm_detail.objects.none()
    if request.method == 'POST':
        system = request.POST["system"]
        alarm_text_ser = request.POST["Alarm_text"]
        if len(alarm_text_ser) > 4:
            if system =="all": 
                search_data = alarm_detail.objects.filter(Q(alarm_description__contains=alarm_text_ser) | Q(alarm_number__contains=alarm_text_ser) | Q(alarm_data__contains=alarm_text_ser)).all() 
            else:
                search_data = alarm_detail.objects.filter(system_type__system_names = system).filter(Q(alarm_description__contains=alarm_text_ser) | Q(alarm_number__contains=alarm_text_ser) | Q(alarm_data__contains=alarm_text_ser)).all() 
        else:
            messages.error(request, "Kindly Search via entering more than 4 char")        
    return render(request, "servicesupport/alarmbytext.html",{
        "flag": 6,
        "product_type":product_type,
        "search_data":search_data,
        "system":system,
        "alarm_text_ser":alarm_text_ser,
    }) 

def alarmbyled(request):
    return render(request, "servicesupport/sevensegment.html",{
        "flag": 6,
        "LED_data":"FF",
    }) 

def spec(request):
    searchvalue = None
    samespec = None
    n= None
    store3 = equ.objects.none() 
    store4 = equ.objects.none() 
    if request.method == 'POST':
        specno = request.POST["specno"] 
        searchvalue = specification.objects.filter(parentspec__icontains = specno).all()
        list = searchvalue.values_list('parentspec',flat=True)
        list1 = searchvalue.values_list('childspec',flat=True)
        n= len(list)

        c=1
        samespec = [1]   
        for t in range(n-1): # gettitng number same parent spec
            if list[t] == list[t+1]:
                c=c+1
                if t == (n-2):
                    samespec.append(c+1)
            else:
                samespec.append(c+1)
                c=c+1
               
        if len(specno) >= 13:
            for s in list1:
                searchvalue3 = equ.objects.filter(spec__icontains = s).exclude(reuse__exact='',info__exact='',equspec__exact='',srno__exact='', trno__exact='').all()
                searchvalue4 = equ.objects.filter(equspec__icontains = s).all()  #.exclude(reuse__isnull=True).exclude(reuse__exact='').exclude(info__isnull=True).exclude(info__exact='').exclude(equspec__isnull=True).exclude(equspec__exact='').exclude(srno__isnull=True).exclude(srno__exact='').exclude(trno__isnull=True).exclude(trno__exact='').all()
                store3 = store3 | searchvalue3 # Child part sepc equ serch
                store4 = store4 | searchvalue4 # Child part sepc reverse equ serch  

    return render(request, "servicesupport/specification.html",{
        "flag": 7, # active tag 
        "serchvalue": searchvalue, # sending data
        "samespec": samespec, #sending same spec to eliminate multi pule time return value
        "n": n, #sending list count
        "store3":store3,
        "store4":store4,
    })

def equivalent(request):
    searchvalue = equ.objects.none() #take Spec input & serch in main spec list
    searchvalue1 = equ.objects.none() #take Spec input & serch in equ spec list for any past update
    availpareant = equ.objects.none() #take spec input & serch if serch avilable in parent spc
    if request.method == 'POST':
        specno = request.POST["specno"] 
        searchvalue = equ.objects.filter(spec__icontains = specno).all()
        
        if len(specno) > 5:
            searchvalue1 = equ.objects.filter(equspec__icontains = specno).all() 
            availpareant = specification.objects.filter(childspec__icontains = specno).all()
        else:    
            messages.info(request, "for Reverce Spec & Part contain in parent search via entering 5 char")    

    return render(request, "servicesupport/equ.html",{
        "flag": 7, # active tag 
        "serchvalue": searchvalue, # sending data equ 
        "serchvalue1": searchvalue1, # sending data Reverce equ serarch  
        "availparent": availpareant, # sending data child in parent spec     
    })

def Spec_details(request,part_id):
    store3 = equ.objects.none() 
    store4 = equ.objects.none() 
    Part_id = int(part_id)
    Search_key = specification.objects.filter(id=part_id).values_list('parentspec',flat=True)
    Main_data= specification.objects.filter(parentspec__exact=Search_key[0]).all()

    list1 = Main_data.values_list('childspec',flat=True)
    for s in list1:
        searchvalue3 = equ.objects.filter(spec__exact = s).exclude(reuse__exact='',info__exact='',equspec__exact='',srno__exact='', trno__exact='').all()
        searchvalue4 = equ.objects.filter(equspec__exact = s).all()  #.exclude(reuse__isnull=True).exclude(reuse__exact='').exclude(info__isnull=True).exclude(info__exact='').exclude(equspec__isnull=True).exclude(equspec__exact='').exclude(srno__isnull=True).exclude(srno__exact='').exclude(trno__isnull=True).exclude(trno__exact='').all()
        store3 = store3 | searchvalue3 # Child part sepc equ serch
        store4 = store4 | searchvalue4 # Child part sepc reverse equ serc

    return render(request, "servicesupport/specificationdetails.html",{
        "flag": 7, # active tag 
        "Main_data":Main_data,
        "store3":store3,
        "store4":store4,
    })    




def specrequest(request):
    if request.method == 'POST' and request.user.is_authenticated:
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
            data = requesttype(request= "Specification", requestadd= requestadd, date=date, user=user, shortdetail= shortdetail, details = data)
            data.save()
            messages.success(request, "Your request added, Thank you for improvement")
        else:
            messages.error(request, "Your request not added, Plese enter Spec more than 10 Char or add details")    
        return render(request, "servicesupport/specrequest.html",{
            "flag": 7, # active tag
            "thisdict":thisdict, # passing form      
            })
    else:    
        return render(request, "servicesupport/specrequest.html",{
            "flag": 7, # active tag      
        })

def ladder(request):
    return render(request, "servicesupport/Index.html",{
        "flag": 8,
    })
def  controls(request):
    return render(request, "servicesupport/Index.html",{
        "flag": 9,
    })        

def manuals(request):
    Manualdata = manual.objects.none()
    Product = manual.objects.values_list('Product_name',flat=True).distinct()
    Product_withManul = system_types.objects.filter(id__in=Product).all()
    if request.method == 'POST':
        system = request.POST["Selection"]
        Manualdata = manual.objects.filter(Product_name__system_names = system).all().order_by('Manual_Name').all()
        
    return render(request,"servicesupport/manual.html",{
        "flag":10,
        "manual":Manualdata,
        "product":Product_withManul,
    })   

def admin_data(request):
    Manualdata = equ.objects.none()
    dupes = equ.objects.values('spec').annotate(Count('id')).order_by().filter(id__count__gt=1)
    data = equ.objects.filter(spec__in=[item['spec'] for item in dupes])
    
    return render(request,"servicesupport/manual.html",{
        "flag":10,
        "data":data,
        "dupes":dupes,
    }) 

# Create your views here.
=======
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Count
import re

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
)


def login_view(request):
    if request.method == "POST":
        # user name data
        username = (request.POST["username"]).lower()
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        print(user)
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


# to check Valid mail id
def Email_check(email):
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
    if re.fullmatch(regex, email):
        return True
    else:
        return False


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
    page_obj = None
    user_data = {"Training": None, "Product": None, "limit": None}
    search_data = Training_model.objects.none()
    Product = Training_model.objects.values_list("Product_name", flat=True).distinct()
    Product_with_Training = product_type.objects.filter(id__in=Product).all()
    if "Product" in request.GET and request.GET["Product"]:
        Product_Ser = request.GET["Product"]
        Training_Data_ser = request.GET["Training_Data"]
        limit = request.GET["limit"]
        user_data = {
            "Training": Training_Data_ser,
            "Product": Product_Ser,
            "limit": limit,
        }
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
        "servicesupport/training.html",
        {
            "flag": 4,
            "product_type": Product_with_Training,
            "page_obj": page_obj,
            "User_input": user_data,
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
    return render(
        request,
        "servicesupport/vrdy.html",
        {
            "flag": 5,
        },
    )


@login_required
def softwn69(request):
    return render(
        request,
        "servicesupport/wn69.html",
        {
            "flag": 5,
        },
    )


@login_required
def softnmi(request):
    return render(
        request,
        "servicesupport/nmi.html",
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
        User_input = {"system": system, "alarm": alarm_text_ser, "limit": limit}

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
    page_obj = None
    User_input = {"specno": None, "limit": None}

    if "specno" in request.GET and request.GET["specno"]:
        specno = request.GET["specno"]
        limit = request.GET["limit"]
        User_input = {"specno": specno, "limit": limit}
        search_value = specification.objects.filter(parentspec__contains=specno).all()
        paginator = Paginator(search_value, limit)
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
        "servicesupport/specification.html",
        {
            "flag": 7,  # active tag
            "page_obj": page_obj,
            "user_data": User_input,
        },
    )


@login_required
def equivalent(request):
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
def admin_data(request):
    dupes = (
        equ.objects.values("spec")
        .annotate(Count("id"))
        .order_by()
        .filter(id__count__gt=1)
    )
    data = equ.objects.filter(spec__in=[item["spec"] for item in dupes])

    return render(
        request,
        "servicesupport/manual.html",
        {
            "flag": 10,
            "data": data,
            "dupes": dupes,
        },
    )


# Create your views here.
>>>>>>> master
