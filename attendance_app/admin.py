from django.contrib import admin
from .models import Attendance

class AttendanceModel (admin.ModelAdmin):
    list_display=('sap_id','start_date_time','end_date_time','attendance_type','start_image','end_image')
    readonly_fields=('created_at','updated_at')
    search_fields = ('sap_id','start_date_time')
admin.site.register(Attendance,AttendanceModel)
