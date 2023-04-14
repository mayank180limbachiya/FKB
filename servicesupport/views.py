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
