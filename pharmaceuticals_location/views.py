import json
from operator import itemgetter
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from delivery_app.models import DeliveryInfoModel
from delivery_app.serializers import DeliverySerializer
from itertools import groupby
from datetime import datetime
import pytz

from pharmaceuticals_location.coustom_data_model import SavePharmaceuticalsLocationData

@api_view(['POST'])
def save_pharmaceuticals_location(request):
    if request.method == 'POST':
        try:        
            data = SavePharmaceuticalsLocationData.from_dict(request.data)
            print(data.to_dict)
            print(f'Your lat: {data.latitude}')
            print(f'Your lon: {data.longitude}')            
            return Response({"success": True},status=status.HTTP_200_OK)
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

