from django.shortcuts import render
from .models import VisitHistoryModel
from .serializers import VisitHistorySerializer,VisitTypeSerializer
from .models import VisitType
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view

# Create your views here.
class VisitHistoryCreateView(generics.ListCreateAPIView):
    queryset = VisitHistoryModel.objects.all()
    serializer_class = VisitHistorySerializer
    
class VisitTypeView(APIView):
    def get(self, request):
        visit_types = [{'key': choice.name, 'value': choice.value} for choice in VisitType]
        serializer = VisitTypeSerializer(visit_types, many=True)
        return Response(serializer.data)