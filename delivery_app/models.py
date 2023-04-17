from django.db import models
import os
from django.db import models

class DeliveryModel(models.Model):
    id = models.AutoField(primary_key=True)
    billing_doc_no = models.CharField(unique=True,max_length=10,null=False)
    billing_date = models.DateField(null=False)
    partner = models.CharField(max_length=10,null=False)
    gate_pass_no = models.CharField(max_length=10,null=False)
    da_code = models.CharField(max_length=8,null=False)
    vehicle_no = models.CharField(max_length=25,null=True)
    route_code = models.CharField(max_length=6,null=True)
    received_date_time = models.DateTimeField(null=True,blank=True)
    latitude = models.DecimalField(max_digits=27, decimal_places=16,null=True)
    longitude = models.DecimalField(max_digits=27, decimal_places=16,null=True)
    class TransportType(models.TextChoices):
        V0 = 'Car', 'Car'
        V1 = 'Walk', 'Walk'
        V2 = 'Rickshaw', 'Rickshaw'
    transport_type = models.CharField(max_length=20,choices=TransportType.choices,null=True)
    class DeliveryStatus(models.TextChoices):
        V0 = 'Pending', 'Pending'
        V1 = 'Cancel', 'Cancel'
        V2 = 'Done', 'Done'
    delivery_status = models.CharField(max_length=20,choices=DeliveryStatus.choices,null=True)
    cash_collection = models.DecimalField(max_digits=8, decimal_places=2,null=True)
    class CollectionStatus(models.TextChoices):
        V0 = 'Pending', 'Pending'
        V1 = 'Cancel', 'Cancel'
        V2 = 'Done', 'Done'
    collection_status = models.CharField(max_length=20,choices=CollectionStatus.choices,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)

    def __str__(self):
        return self.billing_doc_no
    
    class Meta:
        db_table = "rdl_delivery"
        verbose_name = "Delivery"
        verbose_name_plural = "Delivery"

class DeliveryListModel(models.Model):
    id = models.AutoField(primary_key=True)
    delivery = models.ForeignKey(DeliveryModel,on_delete=models.CASCADE,related_name="deliverys",null=False)
    matnr = models.CharField(max_length=40,null=False)
    batch = models.CharField(max_length=10,null=True)
    quantity = models.DecimalField(max_digits=8, decimal_places=2,null=True)
    tp = models.DecimalField(max_digits=8, decimal_places=2,null=True)
    vat = models.DecimalField(max_digits=8, decimal_places=2,null=True)
    net_val = models.DecimalField(max_digits=8, decimal_places=2,null=True)
    received_quantity = models.DecimalField(max_digits=8, decimal_places=2,null=True)
    received_net_val = models.DecimalField(max_digits=8, decimal_places=2,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)

    def __str__(self):
        return self.matnr
    
    class Meta:
        db_table = "rdl_delivery_list"
        verbose_name = "Delivery List"
        verbose_name_plural = "Delivery List"


class DeliveryInfoModel(models.Model):
    billing_doc_no = models.TextField(blank=True,primary_key=True)
    billing_date = models.TextField(blank=True)
    delv_no = models.TextField(blank=True)
    route = models.TextField(blank=True)
    vehicle_no = models.TextField(blank=True)
    da_code = models.TextField(blank=True)
    da_name = models.TextField(blank=True)
    route_name = models.TextField(blank=True)
    billing_type = models.TextField(blank=True)
    partner = models.TextField(blank=True)
    matnr = models.TextField(blank=True)
    quantity = models.TextField(blank=True)
    tp = models.TextField(blank=True)
    vat = models.TextField(blank=True)
    net_val = models.TextField(blank=True)
    assigment = models.TextField(blank=True)
    gate_pass_no = models.TextField(blank=True)
    batch = models.TextField(blank=True)
    plant = models.TextField(blank=True)
    team = models.TextField(blank=True)
    created_on = models.TextField(blank=True)
    material_name = models.TextField(blank=True)
    brand_description = models.TextField(blank=True)
    brand_name = models.TextField(blank=True)
    customer_name = models.TextField(blank=True)
    customer_address = models.TextField(blank=True)
    customer_mobile = models.TextField(blank=True)
    latitude = models.TextField(blank=True)
    longitude = models.TextField(blank=True)
    received_quantity = models.TextField(blank=True)
    delivery_status = models.TextField(blank=True)
    cash_collection = models.TextField(blank=True)
    collection_status = models.TextField(blank=True)

    class Meta:
        managed = False
