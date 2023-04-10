from rest_framework import serializers
from  .models import Attendance

class AttendanceInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        # fields = '__all__'
        fields = ['sap_id','start_date_time','attendance_type','start_latitude','end_latitude','start_image']
