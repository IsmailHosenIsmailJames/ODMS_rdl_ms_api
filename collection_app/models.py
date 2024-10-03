from django.db import models
from delivery_app.models import DeliveryModel

class CashCollectionInfoModel(models.Model):
    id = models.TextField(blank=True,primary_key=True)
    invoice_date = models.TextField(blank=True)
    customer_name = models.TextField(blank=True)
    customer_addreess = models.TextField(blank=True)
    customer_mobile = models.TextField(blank=True)
    delevery_type = models.TextField(blank=True)
    route_name = models.TextField(blank=True)
    latitude = models.TextField(blank=True)
    longitude = models.TextField(blank=True)
    status = models.TextField(blank=True)
    product_code = models.TextField(blank=True)
    product_name = models.TextField(blank=True)
    qty = models.TextField(blank=True)
    per_price = models.TextField(blank=True)
    total_price = models.TextField(blank=True)
    
    class Meta:
        managed = False



class PaymentHistory(models.Model):
    id = models.AutoField(primary_key=True)
    billing_doc_no=models.CharField(max_length=10,null=False)
    partner=models.CharField(max_length=10,null=False)
    da_code=models.CharField(max_length=10,null=False)
    route_code=models.CharField(max_length=6,null=True)
    cash_collection=models.DecimalField(max_digits=8, decimal_places=2,null=True, default=0.00)
    cash_collection_date_time=models.DateTimeField(null=True,blank=True)
    cash_collection_latitude=models.DecimalField(max_digits=27, decimal_places=16,null=True)
    cash_collection_longitude=models.DecimalField(max_digits=27, decimal_places=16,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)
    
    class Meta:
        db_table = "rdl_payment_history"
        verbose_name = "PaymentHistory"
        verbose_name_plural = "PaymentHistory"
        
class ReturnModel(models.Model):
    id=models.AutoField(primary_key=True)
    billing_doc_no=models.CharField(unique=True,max_length=10,null=False)
    billing_date=models.DateField(null=False)
    partner=models.CharField(max_length=10,null=False)
    gate_pass_no = models.CharField(max_length=10,null=False)
    da_code = models.CharField(max_length=8,null=False)
    route_code = models.CharField(max_length=6,null=True)
    return_date_time = models.DateTimeField(null=True,blank=True)
    return_latitude = models.DecimalField(max_digits=27, decimal_places=16,null=True)
    return_longitude = models.DecimalField(max_digits=27, decimal_places=16,null=True)
    class ReturnStatus(models.IntegerChoices):
        v0=0,'NO'
        v1=1,'YES'
    return_status = models.CharField(max_length=20,choices=ReturnStatus.choices,null=True,default=0)
    return_amount=models.DecimalField(max_digits=8,decimal_places=2,default=0.00,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)
    
    def __str__(self):
        return self.billing_doc_no
    
    class Meta:
        db_table = "rdl_return"
        verbose_name = "Return"
        verbose_name_plural = "Return"
    
        
        
class ReturnListModel(models.Model):
    id=models.AutoField(primary_key=True)
    matnr=models.CharField(max_length=40,null=False)
    batch=models.CharField(max_length=40,null=False)
    return_quantity = models.DecimalField(max_digits=10,decimal_places=2,null=True)
    return_net_val = models.DecimalField(max_digits=10,decimal_places=2,null=True)
    billing_doc_no=models.CharField(max_length=10,null=False)
    billing_date=models.DateField(null=False)
    partner=models.CharField(max_length=10,null=False)
    gate_pass_no = models.CharField(max_length=10,null=False)
    da_code = models.CharField(max_length=8,null=False)
    route_code = models.CharField(max_length=6,null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)
    
    def __str__(self):
        return f"{self.id} - {self.delivery} - {self.matnr}"
    
    class Meta:
        db_table = "rdl_return_list"
        verbose_name = "Return List"
        verbose_name_plural = "Return List"