from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

@api_view(['GET'])
def dashboard_report(request,sap_id):
    if request.method == 'GET':
        return Response({"success": True, "result": [{
            'delivery_remaining': 20,
            'delivery_done': 5,
            'cash_remaining': 50000,
            'cash_done': 20000,
            'sap_id': sap_id
        }]}, status=status.HTTP_200_OK)
    
