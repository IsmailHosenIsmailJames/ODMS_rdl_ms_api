from datetime import datetime
from django.utils import timezone
from attendance_app.models import AttendanceModel
from attendance_app.serializers import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
import pytz

def get_start_work_details(sap_id):
    try:
        return AttendanceModel.objects.raw("SELECT * FROM rdl_attendance WHERE sap_id=%s AND DATE_FORMAT(start_date_time, '%%Y-%%m-%%d') = CURDATE()",[sap_id])[0]
    except:
        return None
    
def get_end_work_details(sap_id):
    try:
        return AttendanceModel.objects.raw("SELECT * FROM rdl_attendance WHERE sap_id=%s AND DATE_FORMAT(end_date_time, '%%Y-%%m-%%d') = CURDATE()",[sap_id])[0]
    except:
        return None
    
@api_view(['POST'])
def attendance_start_work(request):
    if request.method == 'POST':
        tz_Dhaka = pytz.timezone('Asia/Dhaka')
        sap_id = request.data.get('sap_id')
        start_work_details = get_start_work_details(sap_id)
        if start_work_details == None:
            serializer = AttendanceInputSerializer(data=request.data)
            if serializer.is_valid():
                serializer.validated_data['start_date_time'] = datetime.now(tz_Dhaka)
                serializer.save()
                return Response({"success": True, "result": serializer.data}, status=status.HTTP_200_OK)
            return Response({"success": False, "message": serializer.errors}, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": 'Already start work'}, status=status.HTTP_200_OK)
    
@api_view(['PUT'])
def attendance_end_work(request,sap_id):
    if request.method == 'PUT':
        tz_Dhaka = pytz.timezone('Asia/Dhaka')
        end_work_details = get_end_work_details(sap_id)
        if end_work_details == None:
            start_work_details = get_start_work_details(sap_id)
            if start_work_details == None:
                return Response({"success": False, "message": "Data not found"}, status=status.HTTP_200_OK)
            serializer = AttendanceInputSerializer(start_work_details, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.validated_data['end_date_time'] = datetime.now(tz_Dhaka)
                serializer.save()
                return Response({"success": True, "result": serializer.data}, status=status.HTTP_200_OK)
            return Response({"success": False, "message": serializer.errors}, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": 'Already end work'}, status=status.HTTP_200_OK)