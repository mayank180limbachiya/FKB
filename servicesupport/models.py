from typing import _SpecialForm
from django.db import models
from django.db.models.base import Model

# from django.db.models.deletion import CASCADE
from django.db.models.fields import EmailField
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User,AbstractUser
import os
from django.urls import reverse

#for no of visits
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Create your models here.


class product_type(models.Model):
    product = models.CharField(max_length=20, unique=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product}"


class system_types(models.Model):
    product_name = models.ForeignKey(
        product_type, on_delete=models.CASCADE, related_name="product_details"
    )
    system_names = models.CharField(max_length=20)
    nick_names = models.CharField(max_length=10, default="None")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            "product_name",
            "system_names",
        )

    def __str__(self):
        return f"{self.system_names} | {self.product_name}"


class alarm_detail(models.Model):
    system_type = models.ForeignKey(
        system_types, on_delete=models.CASCADE, related_name="Alarm_system"
    )
    alarm_number = models.CharField(max_length=20)
    alarm_description = models.TextField(max_length=100)
    manual_name_number = models.TextField(
        max_length=400, default="not found", blank=True, null=True
    )
    alarm_data = RichTextField(max_length=500, blank=True, null=True)
    special_tips = RichTextField(max_length=400, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


class alarm_report(models.Model):
    alarm = models.ForeignKey(
        alarm_detail, on_delete=models.CASCADE, related_name="alarm_info"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_data")
    date = models.DateTimeField()
    report = models.CharField(max_length=200)
    report_flag = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user | self.alarm | self.report_flag}"


class manual(models.Model):
    Product_name = models.ForeignKey(
        system_types, on_delete=models.CASCADE, related_name="manual_system"
    )
    Manual_number = models.CharField(max_length=100, blank=True, null=True)
    Manual_Name = models.CharField(max_length=100, blank=True, null=True)
    Manual_storage = models.FileField(upload_to="uploads/manual/")
    comments = models.CharField(max_length=100, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


class led(models.Model):
    Product_name = models.ForeignKey(
        system_types, on_delete=models.CASCADE, related_name="led_system"
    )
    pdf_name = models.CharField(max_length=100, blank=True, null=True)
    pdf_storage = models.FileField(upload_to="uploads/alarm_led/")
    comments = models.CharField(max_length=100, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


CHOICES = (("Training", "Training"), ("Procedure", "Procedure"))


class Training_model(models.Model):
    Product_name = models.ForeignKey(
        product_type, on_delete=models.CASCADE, related_name="Training_product"
    )
    System_name = models.ForeignKey(
        system_types, on_delete=models.CASCADE, related_name="Training_system"
    )
    Training_Name = models.CharField(max_length=100, blank=True, null=True)
    Training_details = models.CharField(max_length=300, blank=True, null=True)
    Training_storage = models.FileField(upload_to="uploads/training/")
    Type = models.CharField(max_length=20, choices=CHOICES, default="Training")
    comments = models.CharField(max_length=100, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


class specification(models.Model):
    parentspec = models.CharField(max_length=55)
    parentname = models.CharField(max_length=100, blank=True, null=True)
    level = models.CharField(max_length=3, blank=True, null=True)
    spec_parent = models.CharField(max_length=50, blank=True, null=True)
    spec_PartsName = models.CharField(max_length=100, blank=True, null=True)
    childspec = models.CharField(max_length=50, blank=True, null=True)
    childname = models.CharField(max_length=100, blank=True, null=True)
    qty = models.IntegerField(blank=True, null=True)
    remarks = models.CharField(max_length=50, blank=True, null=True)
    level_1 = models.CharField(max_length=50, blank=True, null=True)
    hierarchy = models.CharField(max_length=100, blank=True, null=True)
    stockrank = models.CharField(max_length=5, blank=True, null=True)
    mainte_level = models.CharField(max_length=5, blank=True, null=True)
    SpecialSpec = models.CharField(max_length=5, blank=True, null=True)
    RegisteredDate = models.CharField(max_length=20, blank=True, null=True)
    TerminatedDate = models.CharField(max_length=20, blank=True, null=True)
    spare_type = models.CharField(max_length=3, blank=True, null=True)
    old = models.CharField(max_length=3, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


class equ(models.Model):
    spec = models.CharField(max_length=50, blank=False)
    discription = models.CharField(max_length=70, blank=True, null=True)
    reuse = models.BooleanField(blank=True, null=True)
    info = models.CharField(max_length=100, blank=True, null=True)
    equspec = models.CharField(max_length=100, blank=True, null=True)
    srno = models.CharField(max_length=50, blank=True, null=True)
    trno = models.CharField(max_length=50, blank=True, null=True)
    remark = models.CharField(max_length=150, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


class requesttype(models.Model):
    request = models.CharField(max_length=30)  # char form which screen
    requestadd = models.CharField(max_length=30)  # for which data request
    shortdetail = models.CharField(max_length=50)
    details = models.CharField(max_length=200)  # In details  discription
    flag = models.BooleanField(default=False)  # request completed
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # request user
    date = models.DateTimeField()  # request add date
    closedate = models.DateTimeField(blank=True, null=True)  # request completed date
    updated_at = models.DateTimeField(auto_now=True)


class std(models.Model):
    Std_name = models.CharField(max_length=150)
    System_type = models.ForeignKey(system_types, on_delete=models.CASCADE)
    MTB_name = models.CharField(max_length=100, blank=True, null=True)
    Machine_model = models.CharField(max_length=100, blank=True, null=True)
    problem_solved = RichTextField(max_length=1000, blank=True, null=True)
    special_comments = models.CharField(
        max_length=150,
        null=True,
        blank=True,
    )
    Part_used = models.CharField(
        max_length=500,
        null=True,
        blank=True,
    )
    file = models.FileField(upload_to="uploads/STD/")
    updated_at = models.DateTimeField(auto_now=True)

class analytics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    page = models.CharField(max_length=30)
    ip = models.CharField(max_length= 70,null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class spec_details(models.Model):
    spec_no = models.CharField(max_length=50)
    photo= models.ImageField(upload_to='uploads/images/')
    weight = models.IntegerField(max_length=15,null=True,blank=True)
    
    def serialize(self):
        return {
            "id": self.id,
            "spec_no": self.spec_no,
            "weight": self.weight,
            "photo": self.photo.url,
        }