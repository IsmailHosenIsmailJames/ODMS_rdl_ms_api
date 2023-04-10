import os
from django.db import models
from user_app.models import UserList

# lets us explicitly set upload path and filename
def upload_to(instance, filename):
    fileName, fileExtension = os.path.splitext(filename)
    path = "attendance_images/"
    format = str(instance.sap_id) + instance.start_date_time.strftime("%Y%m%d%H%M%S") + fileExtension
    return os.path.join(path, format)

class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    sap_id = models.ForeignKey(UserList,db_column='sap_id',on_delete=models.DO_NOTHING,null=True)
    start_date_time = models.DateTimeField(null=False)
    end_date_time = models.DateTimeField(null=True,blank=True)
    late_time_min = models.IntegerField(null=True,blank=True)
    over_time_min = models.IntegerField(null=True,blank=True)
    class AttendanceType(models.TextChoices):
        V0 = 'Present', 'Present'
        V1 = 'Absent', 'Absent'
        V2 = 'Late', 'Late'
        V3 = 'Overtime', 'Overtime'
    attendance_type = models.CharField(max_length=20,choices=AttendanceType.choices,null=True)
    start_latitude = models.DecimalField(max_digits=27, decimal_places=16,null=True)
    start_longitude = models.DecimalField(max_digits=27, decimal_places=16,null=True)
    end_latitude = models.DecimalField(max_digits=27, decimal_places=16,null=True,blank=True)
    end_longitude = models.DecimalField(max_digits=27, decimal_places=16,null=True,blank=True)
    start_image = models.ImageField(upload_to=upload_to, null=True,blank=True)
    end_image = models.ImageField(upload_to=upload_to, null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)

    def __str__(self):
        return str(self.sap_id)
    
    class Meta:
        db_table = "rdl_attendance"
        verbose_name = "Attendance"
        verbose_name_plural = "Attendance"