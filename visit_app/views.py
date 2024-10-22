from django.shortcuts import render
from .models import VisitHistoryModel
from .serializers import VisitHistorySerializer
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

# Create your views here.
class VisitHistoryCreateView(generics.ListCreateAPIView):
    queryset = VisitHistoryModel.objects.all()
    serializer_class = VisitHistorySerializer