from django.forms import model_to_dict
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from user_app.models import UserList, AdminUserList
from user_app.serializers import *
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from attendance_app.models import AttendanceModel
from django.db.models import Q

# Create your views here.

def user_login_details(sap_id):
    try:
        return UserList.objects.get(sap_id=sap_id)
    except UserList.DoesNotExist:
        return None
    
def user_login_check(sap_id,password):
    try:
        return UserList.objects.get(sap_id=sap_id,password=password)
    except UserList.DoesNotExist:
        return None

def user_admin_login_check(user_name,password):
    try:
        return AdminUserList.objects.get(user_name=user_name,password=password)
    except AdminUserList.DoesNotExist:
        return None
        
def get_start_work_details(sap_id):
    try:
        return AttendanceModel.objects.raw("SELECT * FROM rdl_attendance WHERE sap_id=%s AND DATE_FORMAT(start_date_time, '%%Y-%%m-%%d') = CURDATE()",[sap_id])[0]
    except:
        return None
    
@api_view(['GET'])
def user_list(request):
    if request.method == 'GET':
        user_list = UserList.objects.all()
        if user_list.exists():
            serializer = UserDetailsSerializer(user_list, many=True)
            return Response({"success": True, "result": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"success": False, "message": 'Your user list is not available'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def user_admin_login(request):
    if request.method == 'POST':
        user_name = request.data.get('user_name')
        password = request.data.get('password')
        login_check = user_admin_login_check(user_name,password)
        if login_check == None:
            return Response({"success": False, "message": 'Your user name or password not match'}, status=status.HTTP_200_OK)
        else:
            serializer = AdminUserDetailsSerializer(login_check, many=False)
            return Response({"success": True, "result": serializer.data}, status=status.HTTP_200_OK)
        
@api_view(['POST'])
def user_login(request):
    if request.method == 'POST':
        sap_id = request.data.get('sap_id')
        password = request.data.get('password')
        login_check = user_login_check(sap_id,password)
        if login_check == None:
            return Response({"success": False, "message": 'Your sap id or password not match'}, status=status.HTTP_200_OK)
        else:
            is_start_work = False
            start_work_details = get_start_work_details(sap_id)
            if start_work_details != None:
                is_start_work = True
            serializer = UserDetailsSerializer(login_check, many=False)
            return Response({"success": True, "result": serializer.data, "is_start_work": is_start_work}, status=status.HTTP_200_OK)
            
@api_view(['POST'])
def user_registration(request):
    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "result": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
def user_details(request):
    if request.method == 'GET':
        sap_id = request.query_params.get("sap_id")
        user_details = user_login_details(sap_id)
        if user_details == None:
            return Response({"success": False, "message": 'User not found'}, status=status.HTTP_200_OK)
        else:
            is_start_work = False
            start_work_details = get_start_work_details(sap_id)
            if start_work_details != None:
                is_start_work = True
            serializer = UserDetailsSerializer(user_details, many=False)
            return Response({"success": True, "result": serializer.data, "is_start_work": is_start_work}, status=status.HTTP_200_OK)
        

@api_view(['POST'])
def admin_user_list(request):
    if request.method == 'POST':
        try:
            offset = int(request.data.get('offset', 0))
            limit = int(request.data.get('limit', 10))
            filters = request.data.get('filters', {})
            filter_type = request.data.get('filter_type', [])
            query = Q(status=1)
            for filter_item in filter_type:
                key = filter_item.get('key')
                value = filters.get(key, '')
                if value and filter_item.get('is_search'):
                    search_type = filter_item.get('search_type')
                    if search_type == 'like':
                        query &= Q(**{f'{key}__icontains': value})
                    elif search_type == 'equals':
                        query &= Q(**{f'{key}': value})

            get_data = UserList.objects.filter(query).order_by('sap_id')[offset:offset+limit]
            total_row = UserList.objects.filter(query).count()

            if not get_data:
                return JsonResponse({'success': False, 'message': 'Data not found'})
            else:
                return JsonResponse({'success': True, 'result': list(get_data.values()), 'total_row': total_row})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
        
@api_view(['POST'])
def admin_insert_user(request):
    if request.method == 'POST':
        try:
            insert_data = UserList.objects.create(**request.data)
            return JsonResponse({'success': True, 'result': model_to_dict(insert_data)})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

@api_view(['POST'])
def admin_update_user(request):
    if request.method == 'POST':
        try:
            _id = request.data.get('id')
            get_data = UserList.objects.get(id=_id)
            print(_id)
            for key, value in request.data.items():
                setattr(get_data, key, value)
            get_data.save()
            return JsonResponse({'success': True, 'result': model_to_dict(get_data)})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

@api_view(['POST'])
def admin_delete_user(request):
    if request.method == 'POST':
        try:
            _id = request.data.get('del_id')
            get_data = UserList.objects.get(id=_id)
            get_data.delete()
            return JsonResponse({'success': True, 'result': 'Deleted successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})