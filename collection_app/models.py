from django.db import models

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
    billing_doc_no=models.CharField(unique=True, max_length=10,null=False)
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