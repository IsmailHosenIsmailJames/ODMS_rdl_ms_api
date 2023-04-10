from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from attendance_app.models import UserList
from attendance_app.serializers import *
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser, FormParser

@api_view(['POST'])
def attendance_start_work(request):
    if request.method == 'POST':
        serializer = AttendanceInputSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)