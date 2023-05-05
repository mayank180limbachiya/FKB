<<<<<<< HEAD
from django.db import models
from import_export import resources, fields
from .models import equ, specification , alarm_detail, system_types,manual,Training_model,product_type
from import_export.widgets import ForeignKeyWidget

class specificationResource(resources.ModelResource):
    class Meta:
        model = specification

class alarmsdetailResource(resources.ModelResource):
    system_type = fields.Field(column_name='system_type',
        attribute='system_type',
        widget=ForeignKeyWidget(system_types, 'system_names'))
    class Meta:
        model = alarm_detail       

class equResource(resources.ModelResource):
    class Meta:
        model = equ        

class manualResource(resources.ModelResource):
    class Meta:
        model = manual

class Training_modelResource(resources.ModelResource):
    Product_name = fields.Field(column_name='Product_name',
        attribute='Product_name',
        widget=ForeignKeyWidget(product_type, 'product'))
    class Meta:
        model = Training_model
=======
from django.db import models
from import_export import resources, fields
from .models import (
    equ,
    specification,
    alarm_detail,
    system_types,
    manual,
    Training_model,
    product_type,
)
from import_export.widgets import ForeignKeyWidget


class specificationResource(resources.ModelResource):
    class Meta:
        model = specification


class alarmsdetailResource(resources.ModelResource):
    system_type = fields.Field(
        column_name="system_type",
        attribute="system_type",
        widget=ForeignKeyWidget(system_types, "system_names"),
    )

    class Meta:
        model = alarm_detail


class equResource(resources.ModelResource):
    class Meta:
        model = equ


class manualResource(resources.ModelResource):
    class Meta:
        model = manual


class Training_modelResource(resources.ModelResource):
    Product_name = fields.Field(
        column_name="Product_name",
        attribute="Product_name",
        widget=ForeignKeyWidget(product_type, "product"),
    )

    class Meta:
        model = Training_model
>>>>>>> master
