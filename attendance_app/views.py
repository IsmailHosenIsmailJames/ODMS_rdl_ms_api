from django.http import JsonResponse
from django.utils import timezone
from attendance_app.models import AttendanceModel
from attendance_app.serializers import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime
import pytz
from django.db.models import Q
from datetime import datetime, time

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
                current_time = datetime.now(tz_Dhaka)
                last_allowed_time = time(9, 10)  # 09:10 AM

                # Calculate late time if the current time exceeds the allowed time
                if current_time.time() > last_allowed_time:
                    late_time_min = (current_time.hour - 9) * 60 + (current_time.minute - 10)
                else:
                    late_time_min = 0
                    
                serializer.validated_data['start_date_time'] = datetime.now(tz_Dhaka)
                serializer.validated_data['late_time_min'] = late_time_min
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
        

@api_view(['POST'])
def admin_attendance_list(request):
    if request.method == 'POST':
        try:
            offset = int(request.data.get('offset', 0))
            limit = int(request.data.get('limit', 10))
            filters = request.data.get('filters', {})
            filter_type = request.data.get('filter_type', [])
            query = Q()
            for filter_item in filter_type:
                key = filter_item.get('key')
                value = filters.get(key, '')
                if value and filter_item.get('is_search'):
                    search_type = filter_item.get('search_type')
                    if search_type == 'like':
                        query &= Q(**{f'{key}__icontains': value})
                    elif search_type == 'equals':
                        query &= Q(**{f'{key}': value})

            get_data = AttendanceModel.objects.filter(query).order_by('-id')[offset:offset+limit]
            total_row = AttendanceModel.objects.filter(query).count()

            if not get_data:
                return JsonResponse({'success': False, 'message': 'Data not found'})
            else:
                return JsonResponse({'success': True, 'result': list(get_data.values()), 'total_row': total_row})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
        