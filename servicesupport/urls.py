from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),  # flag 1
    path("login", views.login_view, name="login"),  # flag 12
    path("logout", views.logout_view, name="logout"),  # flag 13
    path("register", views.register, name="register"),  # flag 2
    path("lostpassword", views.lostpassword, name="lostpassword"),  # flag 2
    path("std", views.std, name="std"),  # flag 3
    path("training", views.training, name="training"),  # flag 4
    path("softwaretool", views.softwaretool, name="softwaretool"),  # flag 5
    path("softwaretool/VRDY", views.softvrdy, name="vrdy"),  # flag 5
    path("softwaretool/wn69", views.softwn69, name="wn69"),  # flag 5
    path("softwaretool/NMI", views.softnmi, name="nmi"),  # flag 5
    path("alarm", views.alarm, name="alarm"),  # flag 6
    path("alarm/bynumber", views.alarmbynumber, name="alarmbynumber"),  # flag 6
    path("alarm/text", views.alarmbytext, name="alarmbytext"),  # flag 6
    path("alarm/LED", views.alarmbyled, name="alarmbyled"),  # flag 6
    path("specification", views.spec, name="specification"),  # flag 7
    path("specification/equ", views.equivalent, name="equ"),  # flag 7
    path("specification/request", views.specrequest, name="specrequest"),  # flag 7
    path("manuals", views.manuals, name="manual"),  # flag 10
    path("manuals/view", views.manualsview, name="manualview"),  # flag 10
    path("admin_data", views.admin_data, name="admin_data"),  # flag 10
    path("specification/<str:part_id>", views.Spec_details, name="spec_details"),
]
