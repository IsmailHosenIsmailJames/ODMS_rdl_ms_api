import decimal
from operator import itemgetter
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from itertools import groupby
import pytz
from delivery_app.models import DeliveryInfoModel, DeliveryModel
from delivery_app.serializers import DeliverySerializer
from datetime import datetime
from django.db import connection

def execute_raw_query(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        results = cursor.fetchall()
    return results

@api_view(['GET'])
def cash_collection_list_v2(request,sap_id):
    if request.method == 'GET':
        d_type = request.query_params.get("type")
        query = " AND d.delivery_status = 'Done' "
        if d_type == 'All':
            query = query
        elif d_type == 'GatePass':
            query = ""
        elif d_type == 'Return':
            query = " AND d.delivery_status = 'Done' AND dl.return_net_val > 0"
        elif d_type == 'Due':
            query = " AND d.delivery_status = 'Done' AND d.delivery_status = 'Done' AND d.cash_collection_status = 'Done' AND d.due_amount > 1"
        elif d_type == 'Remaining':
            query = query + "AND d.cash_collection_status IS NULL"
        else:
            query = query + "AND d.cash_collection_status = '"+d_type+"'"

        sql = "SELECT dis.*,IFNULL(rs.description, 'No Route Name') AS route_name, " \
                "sis.billing_type,sis.partner,sis.matnr,sis.quantity,sis.tp,sis.vat,sis.net_val,sis.assigment,sis.gate_pass_no,sis.batch,sis.plant,sis.team,sis.created_on, " \
                "m.material_name,m.brand_description,m.brand_name, " \
                "CONCAT(c.name1,c.name2) customer_name,CONCAT(c.street,c.street1,c.street2) customer_address,c.mobile_no customer_mobile, " \
                "cl.latitude,cl.longitude, " \
                "d.id,dl.id list_id,d.transport_type," \
                "dl.return_quantity,dl.return_net_val,dl.delivery_quantity,dl.delivery_net_val,IF(d.delivery_status IS NULL,'Pending',d.delivery_status) delivery_status,d.cash_collection,IF(d.cash_collection_status IS NULL,'Pending',d.cash_collection_status) cash_collection_status " \
                "FROM rdl_delivery_info_sap dis " \
                "LEFT JOIN rdl_route_sap rs ON dis.route=rs.route " \
                "INNER JOIN rpl_sales_info_sap sis ON dis.billing_doc_no=sis.billing_doc_no " \
                "INNER JOIN rpl_material m ON sis.matnr=m.matnr " \
                "INNER JOIN rpl_customer c ON sis.partner=c.partner " \
                "LEFT JOIN exf_customer_location cl ON sis.partner=cl.customer_id " \
                "LEFT JOIN rdl_delivery d ON sis.billing_doc_no=d.billing_doc_no " \
                "LEFT JOIN rdl_delivery_list dl ON d.id=dl.delivery_id AND sis.matnr=dl.matnr " \
                "WHERE dis.billing_date = CURRENT_DATE() AND dis.da_code = '%s' "+query+" ;"
        
        data_list = DeliveryInfoModel.objects.raw(sql,[sap_id])
        an_iterator = groupby(data_list, lambda x : x.billing_doc_no)
        data = []
        for key, group in an_iterator:
            key_and_group = {key : list(group)}
            sub_data = []
            for item in key_and_group[key]:
                rec_qty = 0
                if item.delivery_quantity is not None:
                    rec_qty = item.delivery_quantity
                rec_net_val = 0
                if item.delivery_net_val is not None:
                    rec_net_val = item.delivery_net_val
                return_quantity = 0
                if item.return_quantity is not None:
                    return_quantity = item.return_quantity
                return_net_val = 0
                if item.return_net_val is not None:
                    return_net_val = item.return_net_val

                sub_data.append({
                    "id": item.list_id,
                    "matnr": item.matnr,
                    "quantity": item.quantity,
                    "tp": item.tp,
                    "vat": item.vat,
                    "net_val": item.net_val,
                    "batch": item.batch,
                    "material_name": item.material_name,
                    "brand_description": item.brand_description,
                    "brand_name": item.brand_name,
                    "delivery_quantity": rec_qty,
                    "delivery_net_val": rec_net_val,
                    "return_quantity": return_quantity,
                    "return_net_val": return_net_val,
                })

                cash_collection = 0
                if key_and_group[key][0].cash_collection is not None:
                    cash_collection = key_and_group[key][0].cash_collection

                
            main_data = {
                "id": key_and_group[key][0].id,
                "billing_doc_no": key_and_group[key][0].billing_doc_no,
                "billing_date": key_and_group[key][0].billing_date,
                "route_code": key_and_group[key][0].route,
                "route_name": key_and_group[key][0].route_name,
                "da_code": key_and_group[key][0].da_code,
                "da_name": key_and_group[key][0].da_name,
                "partner": key_and_group[key][0].partner,
                "customer_name": key_and_group[key][0].customer_name,
                "customer_address": key_and_group[key][0].customer_address,
                "customer_mobile": key_and_group[key][0].customer_mobile,
                "latitude": key_and_group[key][0].latitude,
                "longitude": key_and_group[key][0].longitude,
                "delivery_status": key_and_group[key][0].delivery_status,
                "cash_collection": cash_collection,
                "cash_collection_status": key_and_group[key][0].cash_collection_status,
                "gate_pass_no": key_and_group[key][0].gate_pass_no,
                "vehicle_no": key_and_group[key][0].vehicle_no,
                "transport_type": key_and_group[key][0].transport_type,
                "product_list": sub_data
            }
            data.append(main_data)

            key_func = itemgetter('billing_date', 'partner')
            sorted_data = sorted(data, key=key_func)
            grouped_data = {key: list(group) for key, group in groupby(sorted_data, key=key_func)}
            customer_data = []
            for (billing_date, partner), group in grouped_data.items():
                customer_data.append({
                    "billing_date": group[0]['billing_date'],
                    "route_code": group[0]['route_code'],
                    "route_name": group[0]['route_name'],
                    "da_code": group[0]['da_code'],
                    "da_name": group[0]['da_name'],
                    "partner": group[0]['partner'],
                    "customer_name": group[0]['customer_name'],
                    "customer_address": group[0]['customer_address'],
                    "customer_mobile": group[0]['customer_mobile'],
                    "latitude": group[0]['latitude'],
                    "longitude": group[0]['longitude'],
                    "invoice_list": group,
            })

    return Response({"success": True, "result": customer_data}, status=status.HTTP_200_OK)
    

@api_view(['GET'])
def cash_collection_list(request,sap_id):
    if request.method == 'GET':
        d_type = request.query_params.get("type")
        query = " AND d.delivery_status = 'Done' "
        if d_type == 'All':
            query = query
        elif d_type == 'GatePass':
            query = ""
        elif d_type == 'Return':
            query = " AND d.delivery_status = 'Done' AND d.cash_collection_status = 'Done' AND dl.return_net_val IS NOT NULL"
        elif d_type == 'Due':
            query = " AND d.delivery_status = 'Done' AND d.delivery_status = 'Done' AND d.cash_collection_status = 'Done' AND d.due_amount > 1"
        elif d_type == 'Remaining':
            query = query + "AND d.cash_collection_status IS NULL"
        else:
            query = query + "AND d.cash_collection_status = '"+d_type+"'"

        sql = "SELECT dis.*,rs.description route_name, " \
                "sis.billing_type,sis.partner,sis.matnr,sis.quantity,sis.tp,sis.vat,sis.net_val,sis.assigment,sis.gate_pass_no,sis.batch,sis.plant,sis.team,sis.created_on, " \
                "m.material_name,m.brand_description,m.brand_name, " \
                "CONCAT(c.name1,c.name2) customer_name,CONCAT(c.street,c.street1,c.street2) customer_address,c.mobile_no customer_mobile, " \
                "cl.latitude,cl.longitude, " \
                "d.id,dl.id list_id,d.transport_type," \
                "dl.return_quantity,dl.return_net_val,dl.delivery_quantity,dl.delivery_net_val,IF(d.delivery_status IS NULL,'Pending',d.delivery_status) delivery_status,d.cash_collection,IF(d.cash_collection_status IS NULL,'Pending',d.cash_collection_status) cash_collection_status " \
                "FROM rdl_delivery_info_sap dis " \
                "INNER JOIN rdl_route_sap rs ON dis.route=rs.route " \
                "INNER JOIN rpl_sales_info_sap sis ON dis.billing_doc_no=sis.billing_doc_no " \
                "INNER JOIN rpl_material m ON sis.matnr=m.matnr " \
                "INNER JOIN rpl_customer c ON sis.partner=c.partner " \
                "LEFT JOIN exf_customer_location cl ON sis.partner=cl.customer_id " \
                "LEFT JOIN rdl_delivery d ON sis.billing_doc_no=d.billing_doc_no " \
                "LEFT JOIN rdl_delivery_list dl ON d.id=dl.delivery_id AND sis.matnr=dl.matnr " \
                "WHERE dis.billing_date = CURRENT_DATE() AND dis.da_code = '%s' "+query+" ;"
        
        data_list = DeliveryInfoModel.objects.raw(sql,[sap_id])
        an_iterator = groupby(data_list, lambda x : x.billing_doc_no)
        data = []
        for key, group in an_iterator:
            key_and_group = {key : list(group)}
            sub_data = []
            for item in key_and_group[key]:
                rec_qty = 0
                if item.delivery_quantity is not None:
                    rec_qty = item.delivery_quantity
                rec_net_val = 0
                if item.delivery_net_val is not None:
                    rec_net_val = item.delivery_net_val
                return_quantity = 0
                if item.return_quantity is not None:
                    return_quantity = item.return_quantity
                return_net_val = 0
                if item.return_net_val is not None:
                    return_net_val = item.return_net_val

                sub_data.append({
                    "id": item.list_id,
                    "matnr": item.matnr,
                    "quantity": item.quantity,
                    "tp": item.tp,
                    "vat": item.vat,
                    "net_val": item.net_val,
                    "batch": item.batch,
                    "material_name": item.material_name,
                    "brand_description": item.brand_description,
                    "brand_name": item.brand_name,
                    "delivery_quantity": rec_qty,
                    "delivery_net_val": rec_net_val,
                    "return_quantity": return_quantity,
                    "return_net_val": return_net_val,
                })

                cash_collection = 0
                if key_and_group[key][0].cash_collection is not None:
                    cash_collection = key_and_group[key][0].cash_collection

                
            main_data = {
                "id": key_and_group[key][0].id,
                "billing_doc_no": key_and_group[key][0].billing_doc_no,
                "billing_date": key_and_group[key][0].billing_date,
                "route_code": key_and_group[key][0].route,
                "route_name": key_and_group[key][0].route_name,
                "da_code": key_and_group[key][0].da_code,
                "da_name": key_and_group[key][0].da_name,
                "partner": key_and_group[key][0].partner,
                "customer_name": key_and_group[key][0].customer_name,
                "customer_address": key_and_group[key][0].customer_address,
                "customer_mobile": key_and_group[key][0].customer_mobile,
                "latitude": key_and_group[key][0].latitude,
                "longitude": key_and_group[key][0].longitude,
                "delivery_status": key_and_group[key][0].delivery_status,
                "cash_collection": cash_collection,
                "cash_collection_status": key_and_group[key][0].cash_collection_status,
                "gate_pass_no": key_and_group[key][0].gate_pass_no,
                "vehicle_no": key_and_group[key][0].vehicle_no,
                "transport_type": key_and_group[key][0].transport_type,
                "product_list": sub_data
            }
            data.append(main_data)

        return Response({"success": True, "result": data}, status=status.HTTP_200_OK)


@api_view(['PUT'])
def cash_collection_save(request, pk):
    try:
        delivery = DeliveryModel.objects.get(pk=pk)
    except DeliveryModel.DoesNotExist:
        return Response({"error": "Delivery not found"}, status=status.HTTP_404_NOT_FOUND)

    tz_Dhaka = pytz.timezone('Asia/Dhaka')
    serializer = DeliverySerializer(delivery, data=request.data, partial=True)
    if serializer.is_valid():
        sql = "SELECT SUM(net_val) net_val FROM rpl_sales_info_sap sis WHERE sis.billing_doc_no = %s;"
        billing_doc_no = request.data.get('billing_doc_no')
        result = execute_raw_query(sql,[billing_doc_no])
        serializer.validated_data['net_val']=result[0][0];
        if request.data.get('type') == "cash_collection":
            cash_collection = request.data.get('cash_collection')
            due = float(result[0][0]) - float(cash_collection)
            serializer.validated_data['due_amount']=due;
            serializer.validated_data['cash_collection_date_time'] = datetime.now(tz_Dhaka)
        elif request.data.get('type') == "return":
            serializer.validated_data['return_date_time'] = datetime.now(tz_Dhaka)
        
        serializer.update(delivery, serializer.validated_data)
        
        return Response({"success": True, "result": serializer.data}, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)