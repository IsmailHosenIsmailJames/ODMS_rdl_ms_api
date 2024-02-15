from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from user_app.models import UserList, AdminUserList
from user_app.serializers import *
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from attendance_app.models import AttendanceModel

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