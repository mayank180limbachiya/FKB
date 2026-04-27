from rest_framework import serializers
from .models import *


class CustomAlarmSerializer(serializers.ModelSerializer):
    system_type = serializers.SlugRelatedField(read_only=True,slug_field="system_names")

    class Meta:
        model= alarm_detail
        fields= ("id","system_type","alarm_number","alarm_description","manual_name_number","alarm_data","special_tips",)
        
class CustomSystemsSerializer(serializers.ModelSerializer):
    product_name = serializers.SlugRelatedField(read_only=True,slug_field="product")
    class Meta:
        model= system_types
        fields= ("id","system_names","nick_names","product_name")

class CustomTrainingSerializer(serializers.ModelSerializer):
    product_name = serializers.SlugRelatedField(read_only=True,slug_field="product")
    system_name = serializers.SlugRelatedField(read_only=True,slug_field="system")
    #Training_storage_url = serializers.SerializerMethodField('get_thumbnail_url')

    #def get_thumbnail_url(self, obj):
    #    return self.context['request'].build_absolute_uri(obj.Training_storage)

    class Meta:
        model= Training_model
        fields= ("id","product_name","system_name","Training_Name","Training_details","Training_storage")

class CustomParent_specSerializer(serializers.ModelSerializer):
    class Meta:
        model= specification
        fields= ("id","parentspec","parentname","level","spec_parent","spec_PartsName","childspec","childname","qty","remarks","SpecialSpec")   

class CustomChild_specSerializer(serializers.ModelSerializer):
    class Meta:
        model = equ
        fields = ("id","spec","discription","reuse","info","equspec","srno","trno","remark")

class CustomParent_childSerializer(serializers.ModelSerializer):
    class Meta:
        model = specification
        fields= ("id","parentspec","parentname","level","spec_parent","spec_PartsName","childspec","childname","qty","remarks","SpecialSpec")   

class CustomManualSerializer(serializers.ModelSerializer):
    #Manual_storage = serializers.SerializerMethodField('get_thumbnail_url')
    Product_name = serializers.SlugRelatedField(read_only=True,slug_field="system_names")
    #Training_storage_url = serializers.SerializerMethodField('get_thumbnail_url')
    #def get_thumbnail_url(self, obj):
    #    return self.context['request'].build_absolute_uri(obj.Manual_storage)
    product_name = serializers.SlugRelatedField(read_only=True,slug_field="product")
    class Meta:
        model = manual
        fields = ("product_name","Manual_number","Manual_Name","Manual_storage","Product_name")

class CustomStocksSerializer(serializers.ModelSerializer):
    material = serializers.SlugRelatedField(read_only=True,slug_field="spec_no")
    material_name = serializers.SlugRelatedField(read_only=True,slug_field="description")   
    material = serializers.CharField(source='material.spec_no')
    material_name = serializers.CharField(source='material.description') 
    plant = serializers.SlugRelatedField(read_only=True,slug_field="name")
    storage = serializers.SlugRelatedField(read_only=True,slug_field="name")
    class Meta:
        model = Stock
        fields = ("material","storage","plant","material_name","special_stock","special_stock_number","available","transit","returns")     

