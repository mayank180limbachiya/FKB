from django.contrib import admin
from .models import (
    requesttype,
    alarm_detail,
    alarm_report,
    led,
    equ,
    product_type,
    specification,
    system_types,
    manual,
    Training_model,
    analytics,
    spec_details,links,UserData,Serial_Number,Stock,Storage_loc,Plant,
    STDReport, 
    STDApprovalLog
)

from import_export.admin import ImportExportModelAdmin
from .resources import (
    specificationResource,
    alarmsdetailResource,
    equResource,
    manualResource,
    Training_modelResource,
)

# Register your models here.


@admin.register(product_type)
class product_type(admin.ModelAdmin):
    list_display = ("id", "product")
    pass


admin.site.register(alarm_report)


@admin.register(requesttype)
class requesttype(admin.ModelAdmin):
    list_display = ("request", "flag", "user", "date", "closedate")
    list_filter = [
        ("flag", admin.BooleanFieldListFilter),
    ]
    pass


@admin.register(specification)
class specificationAdmin(ImportExportModelAdmin):
    resource_class = specificationResource
    list_display = ("parentspec", "parentname", "childspec", "childname", "qty")
    search_fields = ("parentspec", "childspec")
    pass


@admin.register(alarm_detail)
class alarmdetailsAdmin(ImportExportModelAdmin):
    resource_class = alarmsdetailResource
    search_fields = ("alarm_number","alarm_description")
    list_display = ("system_type", "alarm_number", "alarm_description")
    pass


@admin.register(equ)
class equAdmin(ImportExportModelAdmin):
    resource_class = equResource
    search_fields = ("spec", "equspec", "discription")
    list_display = ("spec", "equspec", "discription")
    pass


@admin.register(manual)
class manual(ImportExportModelAdmin):
    resource_class = manualResource
    search_fields = ("Manual_number", "Manual_Name")
    list_display = ("Product_name", "Manual_number", "Manual_Name", "Manual_storage")
    pass


@admin.register(Training_model)
class Training_model(ImportExportModelAdmin):
    search_fields = ("Training_Name", "Training_details")
    list_display = ("Product_name", "Training_Name")
    resource_class = Training_modelResource
    pass


@admin.register(system_types)
class system_types(admin.ModelAdmin):
    list_display = ("id", "product_name", "system_names", "nick_names")
    pass


@admin.register(led)
class led(admin.ModelAdmin):
    list_display = ("Product_name", "pdf_name", "comments")
    pass

@admin.register(analytics)
class analytics(admin.ModelAdmin):
    list_display = ("user", "page","updated_at")
    pass

@admin.register(spec_details)
class spec_details(admin.ModelAdmin):
    list_display = ("spec_no","weight")
    pass

@admin.register(links)
class links(admin.ModelAdmin):
    list_display = ("id","name","link_name")
    pass

@admin.register(UserData)
class UserData(admin.ModelAdmin):
    list_display = ("id","user")
    pass

@admin.register(Serial_Number)
class Serial_Number(admin.ModelAdmin):
    list_display = ("id","user","serial_no")
    pass

@admin.register(Stock)
class Stock(admin.ModelAdmin):
    list_display = ("material","plant","available")
    search_fields =["material__spec_no"]
    pass

@admin.register(Storage_loc)
class Storage_loc(admin.ModelAdmin):
    list_display = ("storage_location","name")
    pass

@admin.register(Plant)
class Plant(admin.ModelAdmin):
    list_display = ("name","code","short_name")
    pass

class STDApprovalLogInline(admin.TabularInline):
    model   = STDApprovalLog
    extra   = 0
    readonly_fields = ("action", "actor", "comment", "created_at")
    can_delete      = False

@admin.register(STDReport)
class STDReportAdmin(admin.ModelAdmin):
    list_display    = ("id", "std_number_display", "subject", "product",
                       "status", "prepared_by", "reviewed_by", "created_at")
    list_filter     = ("status", "product")
    search_fields   = ("subject", "end_user", "mr_no", "controller_model")
    readonly_fields = ("created_at", "updated_at", "submitted_at", "approved_at")
    inlines         = [STDApprovalLogInline]
 
    @admin.display(description="STD Number")
    def std_number_display(self, obj):
        return f"STD-{obj.created_at.year}-{obj.id:04d}"