from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from user_app.models import UserList
from user_app.serializers import *
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.

@api_view(['POST'])
def user_login(request):
    if request.method == 'POST':
        sap_id = request.data.get('sap_id')
        password = request.data.get('password')
        try:
            get_user_details = UserList.objects.get(sap_id=sap_id,password=password)
            serializer = UserDetailsSerializer(get_user_details, many=False)
            return Response({"success": True, "result": serializer.data}, status=status.HTTP_200_OK)
        except UserList.DoesNotExist:
            return Response({"success": False, "message": 'Your sap id or password not match'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def user_registration(request):
    if request.method == 'POST':
        serializer = UserDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "result": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)