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

def execute_raw_query_v1(sql, params):
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
    
@api_view(['GET'])
def activity_for_map(request,sap_id,date):
    if request.method == 'GET':
        sql = "SELECT * FROM rdl_delivery WHERE da_code = %s AND created_at LIKE %s;"
        params = [sap_id, f"{date}%"]
        result = execute_raw_query_v1(sql, params)
        return Response({"success": True, "result": result}, status=status.HTTP_200_OK)
    
@api_view(['GET'])
def dashboard_report(request,sap_id):
    if request.method == 'GET':
        # sql= "SELECT " \
	    #         "(SELECT COUNT(DISTINCT dis.billing_doc_no) c FROM rdl_delivery_info_sap dis WHERE dis.billing_date = CURRENT_DATE() AND dis.da_code = '%s') total_delivary," \
	    #         "(SELECT COUNT(*) c FROM rdl_delivery d WHERE d.billing_date = CURRENT_DATE() AND d.da_code = '%s') total_delivary_done, " \
	    #         "(SELECT COUNT(*) c FROM rdl_delivery d WHERE d.billing_date = CURRENT_DATE() AND d.da_code = '%s' AND delivery_status = 'Done' AND cash_collection_status IS NULL) total_collection, " \
        #         "(SELECT COUNT(*) c FROM rdl_delivery d WHERE d.billing_date = CURRENT_DATE() AND d.da_code = '%s' AND cash_collection_status = 'Done') total_collection_done, " \
        #         "(SELECT SUM(sis.net_val) c FROM rdl_delivery_info_sap dis INNER JOIN rpl_sales_info_sap sis ON dis.billing_doc_no=sis.billing_doc_no WHERE dis.billing_date = CURRENT_DATE() AND dis.da_code = '%s') total_gate_pass_amount," \
	    #         "(SELECT SUM(d.cash_collection) c FROM rdl_delivery d WHERE d.billing_date = CURRENT_DATE() AND d.da_code = '%s' AND delivery_status = 'Done' AND cash_collection_status = 'Done') total_collection_amount," \
	    #         "(SELECT SUM(dl.return_net_val) c FROM rdl_delivery d INNER JOIN rdl_delivery_list dl ON d.id=dl.delivery_id WHERE d.billing_date = CURRENT_DATE() AND d.da_code = '%s' AND d.delivery_status = 'Done' AND dl.return_net_val IS NOT NULL) total_return_amount," \
	    #         "(SELECT SUM(dl.return_quantity) c FROM rdl_delivery d INNER JOIN rdl_delivery_list dl ON d.id=dl.delivery_id WHERE d.billing_date = CURRENT_DATE() AND d.da_code = '%s' AND d.delivery_status = 'Done' AND dl.return_quantity IS NOT NULL) total_return_quantity," \
        #         "(SELECT (SUM(sis.net_val) - SUM(DISTINCT d.cash_collection)) c FROM rdl_delivery d INNER JOIN rpl_sales_info_sap sis ON d.billing_doc_no=sis.billing_doc_no WHERE d.billing_date = CURRENT_DATE() AND d.da_code = '%s' AND d.delivery_status = 'Done' AND d.cash_collection_status = 'Done') total_due;"      
        # result = execute_raw_query(sql,[sap_id,sap_id,sap_id,sap_id,sap_id,sap_id,sap_id,sap_id,sap_id])

        sql="SELECT " \
                "COUNT(DISTINCT dis.billing_doc_no) AS total_delivary, " \
                "COUNT(d.id) AS total_delivary_done, " \
                "COUNT(CASE WHEN d.delivery_status = 'Done' AND d.cash_collection_status IS NULL THEN 1 END) AS total_collection, " \
                "COUNT(CASE WHEN d.cash_collection_status = 'Done' THEN 1 END) AS total_collection_done, " \
                "SUM(sis.net_val) AS total_gate_pass_amount, " \
                "SUM(CASE WHEN d.delivery_status = 'Done' AND d.cash_collection_status = 'Done' THEN d.cash_collection ELSE 0 END) AS total_collection_amount, " \
                "SUM(CASE WHEN d.delivery_status = 'Done' AND dl.return_net_val IS NOT NULL THEN dl.return_net_val ELSE 0 END) AS total_return_amount, " \
                "SUM(CASE WHEN d.delivery_status = 'Done' AND dl.return_quantity IS NOT NULL THEN dl.return_quantity ELSE 0 END) AS total_return_quantity, " \
                "(SUM(sis.net_val) - SUM(DISTINCT d.cash_collection)) AS total_due " \
            "FROM " \
                "rdl_delivery_info_sap dis " \
                "LEFT JOIN rdl_delivery d ON dis.billing_doc_no = d.billing_doc_no AND d.billing_date = CURRENT_DATE() AND d.da_code = '%s' " \
                "LEFT JOIN rpl_sales_info_sap sis ON dis.billing_doc_no = sis.billing_doc_no " \
                "LEFT JOIN rdl_delivery_list dl ON d.id = dl.delivery_id " \
            "WHERE " \
                "dis.billing_date = CURRENT_DATE() AND dis.da_code = '%s'"
        result = execute_raw_query(sql,[sap_id,sap_id])

        return Response({"success": True, "result": [{
            'delivery_remaining': result[0][0]-result[0][1],
            'delivery_done': result[0][1],
            'cash_remaining': result[0][2],
            'cash_done': result[0][3],
            'sap_id': sap_id,
            'total_gate_pass_amount': result[0][4],
            'total_collection_amount': result[0][5], 
            'total_return_amount': result[0][6], 
            'total_return_quantity': result[0][7],
            'due_amount_total': result[0][8],
            'previous_day_due': 0
        }]}, status=status.HTTP_200_OK)
    
