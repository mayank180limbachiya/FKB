from django.urls import path,include
from . import views
from rest_framework import routers,serializers,viewsets
from django.conf import settings
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'stocks', views.StockViewSet)

urlpatterns = [
    path("", views.index, name="index"),  # flag 1
    path("login", views.login_view, name="login"),  # flag 12
    path("logout", views.logout_view, name="logout"),  # flag 13
    path("register", views.register, name="register"),  # flag 2
    path("lostpassword", views.lostpassword, name="lostpassword"),  # flag 2
    #path("std", views.std, name="std"), 
    path("training", views.training, name="training"),  # flag 4
    path("softwaretool", views.softwaretool, name="softwaretool"),  # flag 5
    path("softwaretool/VRDY", views.softvrdy, name="vrdy"),  # flag 5
    path("softwaretool/wn69", views.softwn69, name="wn69"),  # flag 5
    path("softwaretool/NMI", views.softnmi, name="nmi"),  # flag 5
    path("softwaretool/belttention", views.belttension, name="belttention"),  # flag 5
    path("alarm", views.alarm, name="alarm"),  # flag 6
    path("alarm/bynumber", views.alarmbynumber, name="alarmbynumber"),  # flag 6
    path("alarm/text", views.alarmbytext, name="alarmbytext"),  # flag 6
    path("alarm/LED", views.alarmbyled, name="alarmbyled"),  # flag 6
    path("specification", views.spec, name="specification"),  # flag 7
    path("specification/equ", views.equivalent, name="equ"),  # flag 7
    path("specification/request", views.specrequest, name="specrequest"),  # flag 7
    path("manuals", views.manuals, name="manual"),  # flag 10
    path("manuals/view", views.manualsview, name="manualview"),  # flag 10
    path("admin_data", views.admin_data, name="admin_data"),  # flag 14
    path("analytic_view", views.analytic_view, name="analytic_view"),
    path("analytic_report", views.analytic_report, name="analytic_report"),
    path("specification/<str:part_id>", views.Spec_details, name="spec_details"),
    path('pdf',views.pdf, name='pdf'),
    path('csv_output',views.csv_output,name='csv_output'),
    path('changepassword',views.changepassword,name='changepassword'),
    path('repair_list',views.repair_list,name='repair_list'),
    path('repair_list/<str:list_id>',views.checklist,name='checklist'),
    path('images/<str:spec>',views.photo,name='images'),
    path('profile',views.profile,name='profile'),
    path('serial_gen',views.serial_gen,name='serial_gen'),
    path('get_latest_serial_number',views.get_latest_serial_number,name="get_latest_serial_number"),

    path('rest/alarm',views.Alarm_search.as_view()),
    path('rest/systems',views.Systems.as_view()),
    path('rest/training',views.Training_search.as_view()),
    path('rest/parentspec',views.Parent_spec.as_view()),
    path('rest/childspec',views.Child_spec.as_view()),
    path('rest/parentspec/<str:part_id>',views.Parent_child.as_view()),
    path('rest/parentavailable',views.Parent_available.as_view()),
    path('rest/manual',views.Manual.as_view()),
    path('stock',views.receive_stock_data, name="stock"),
    path('stocks',views.stocks,name="stocks"),
    path('api/',include(router.urls)),
 
    path("std",                        views.std_list,   name="std"),  # flag 3
    path("std/new",                    views.std_form,   name="std_new"),  # flag 3
    path("std/<int:report_id>/edit",   views.std_form,   name="std_edit"),  # flag 3
    path("std/<int:report_id>",        views.std_detail, name="std_detail"),  # flag 3
    path("std/<int:report_id>/review", views.std_review, name="std_review"), # flag 3
    path("std/import",                  views.std_import,         name="std_import"), # flag 3
    path("std/import/preview",          views.std_import_preview, name="std_import_preview"), # flag 3
] 

if settings.DEBUG :
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)