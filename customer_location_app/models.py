from django.db import models

# Create your models here.

class CustomerLocationModel(models.Model):
    id = models.AutoField(primary_key=True)
    work_area_t = models.CharField(max_length=10, null=True)
    customer_id = models.CharField(max_length=20, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'exf_customer_location'
        indexes = [
            models.Index(fields=['work_area_t']),
            models.Index(fields=['customer_id']),
        ]