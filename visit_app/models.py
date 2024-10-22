from django.db import models
from .constants import VisitType

# Create your models here.
class VisitHistoryModel(models.Model):
    da_code=models.CharField(max_length=10,null=False)
    route_code=models.CharField(max_length=10,null=True)
    partner=models.CharField(max_length=10,null=False)
    visit_type=models.CharField(max_length=50,choices=VisitType,null=False)
    visit_latitude=models.DecimalField(max_digits=27, decimal_places=16,null=True)
    visit_longitude=models.DecimalField(max_digits=27, decimal_places=16,null=True)
    comment=models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)
    
    def __str__(self):
        return f"{self.da_code} - {self.visit_date} - {self.visit_time} - {self.visit_type}"
    
    class Meta:
        db_table = "rdl_visit_history"
        verbose_name = "VisitHistory"
        verbose_name_plural = "VisitHistory"