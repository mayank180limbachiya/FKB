from django.contrib import admin
from .models import requesttype, alarm_detail, alarm_report, equ, product_type, specification, system_types, userdetails ,manual ,Training_model

from import_export.admin import ImportExportModelAdmin
from .resources import specificationResource, alarmsdetailResource , equResource,manualResource , Training_modelResource

# Register your models here.
admin.site.register(userdetails)
admin.site.register(product_type)

admin.site.register(alarm_report)
admin.site.register(requesttype)

@admin.register(specification)
class specificationAdmin(ImportExportModelAdmin):
    resource_class = specificationResource
    list_display = ("parentspec", "parentname", "childspec", "childname","qty")
    search_fields = ("parentspec", "childspec")
    pass

@admin.register(alarm_detail)
class alarmdetailsAdmin(ImportExportModelAdmin):
    resource_class = alarmsdetailResource
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
    list_display = ("Product_name","Manual_number","Manual_Name","Manual_storage")
    pass

@admin.register(Training_model)
class Training_model(ImportExportModelAdmin):
    search_fields = ("Training_Name","Training_details")
    list_display =("Product_name","Training_Name")
    resource_class = Training_modelResource
    pass

@admin.register(system_types)
class system_types(admin.ModelAdmin):
    list_display =("id","product_name","system_names","nick_names")
    pass

