from django.db import models

from django.utils import timezone

class ConveyanceModel(models.Model):
    id = models.AutoField(primary_key=True)
    da_code = models.CharField(max_length=100)
    start_journey_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    start_journey_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    end_journey_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    end_journey_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    start_journey_date_time = models.DateTimeField()
    end_journey_date_time = models.DateTimeField(null=True, blank=True)
    transport_mode = models.TextField(null=True, blank=True) 
    transport_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    journey_status = models.CharField(max_length=20)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Journey {self.id} by {self.da_code}"
    
    class Meta:
        db_table = "rdl_conveyance"
        verbose_name = "Conveyance"
        verbose_name_plural = "Conveyance"

class TransportModeModel(models.Model):
    id = models.AutoField(primary_key=True)
    transport_name = models.CharField(max_length=255)
    class StatusType(models.IntegerChoices):
        V0 = 0, "Inactive"
        V1 = 1, "Active"
    status = models.PositiveSmallIntegerField(choices=StatusType.choices,default=StatusType.V1,null=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True,null=True)

    def __str__(self):
        return self.transport_name
    
    class Meta:
        db_table = "rdl_transport_mode_list"
        verbose_name = "TransportMode"
        verbose_name_plural = "TransportMode"
