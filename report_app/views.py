from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from report_app.models import ReportOneModel
from django.db import connection

def execute_raw_query(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        results = cursor.fetchall()
    return results

@api_view(['GET'])
def dashboard_report(request,sap_id):
    if request.method == 'GET':
        sql= "SELECT " \
            "(SELECT COUNT(DISTINCT dis.billing_doc_no) c FROM rdl_delivery_info_sap dis WHERE dis.billing_date = CURRENT_DATE() AND dis.da_code = '%s') total_delivary," \
            "(SELECT COUNT(*) c FROM rdl_delivery d WHERE d.billing_date = CURRENT_DATE() AND d.da_code = '%s') total_delivary_done, " \
            "(SELECT COUNT(*) c FROM rdl_delivery d WHERE d.billing_date = CURRENT_DATE() AND d.da_code = '%s' AND collection_status = 'Done') total_collection_done;"
        
        result = execute_raw_query(sql,[sap_id,sap_id,sap_id])
        print(result[0][0])

        return Response({"success": True, "result": [{
            'delivery_remaining': result[0][0]-result[0][1],
            'delivery_done': result[0][1],
            'cash_remaining': result[0][0]-result[0][2],
            'cash_done': result[0][2],
            'sap_id': sap_id
        }]}, status=status.HTTP_200_OK)
    
