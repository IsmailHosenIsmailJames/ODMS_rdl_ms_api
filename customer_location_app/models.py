from django.db import models

class CustomerLocationModel(models.Model):
    id = models.AutoField(primary_key=True)
    work_area_t = models.CharField(max_length=10, null=True)
    customer_id = models.CharField(max_length=20, unique=True, null=True)
    latitude = models.DecimalField(max_digits=27, decimal_places=16, null=True, blank=True)
    longitude = models.DecimalField(max_digits=27, decimal_places=16, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rdl_customer_location'
        indexes = [
            models.Index(fields=['work_area_t']),
            models.Index(fields=['customer_id']),
        ]