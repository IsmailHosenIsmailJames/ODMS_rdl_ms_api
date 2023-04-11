from rest_framework import serializers
from  .models import AttendanceModel

class AttendanceInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceModel
        fields = '__all__'
        # fields = ['sap_id','start_date_time','start_latitude','start_longitude','start_image','end_date_time','end_latitude','end_longitude','end_image']
