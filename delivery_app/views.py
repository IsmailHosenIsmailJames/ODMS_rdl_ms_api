from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from delivery_app.models import DeliveryInfoModel
from delivery_app.serializers import DeliverySerializer
from itertools import groupby
from datetime import datetime
import pytz

@api_view(['GET'])
def delivery_list(request,sap_id):
    if request.method == 'GET':
        d_type = request.query_params.get("type")
        sql = "SELECT dis.*,rs.description route_name, " \
                "sis.billing_type,sis.partner,sis.matnr,sis.quantity,sis.tp,sis.vat,sis.net_val,sis.assigment,sis.gate_pass_no,sis.batch,sis.plant,sis.team,sis.created_on, " \
                "m.material_name,m.brand_description,m.brand_name, " \
                "CONCAT(c.name1,c.name2) customer_name,CONCAT(c.street,c.street1,c.street2) customer_address,c.mobile_no customer_mobile, " \
                "cl.latitude,cl.longitude, " \
                "dl.received_quantity,dl.received_net_val,IF(d.delivery_status IS NULL,'Pending',d.delivery_status) delivery_status,d.cash_collection,IF(d.collection_status IS NULL,'Pending',d.collection_status) collection_status " \
                "FROM rdl_delivery_info_sap dis " \
                "INNER JOIN rdl_route_sap rs ON dis.route=rs.route " \
                "INNER JOIN rpl_sales_info_sap sis ON dis.billing_doc_no=sis.billing_doc_no " \
                "INNER JOIN rpl_material m ON sis.matnr=m.matnr " \
                "INNER JOIN rpl_customer c ON sis.partner=c.partner " \
                "LEFT JOIN exf_customer_location cl ON sis.partner=cl.customer_id " \
                "LEFT JOIN rdl_delivery d ON sis.billing_doc_no=d.billing_doc_no " \
                "LEFT JOIN rdl_delivery_list dl ON d.id=dl.delivery_id " \
                "WHERE dis.billing_date = '2023-03-28' AND dis.da_code = '%s';"

    data_list = DeliveryInfoModel.objects.raw(sql,[sap_id])
    an_iterator = groupby(data_list, lambda x : x.billing_doc_no)
    data = []
    for key, group in an_iterator:
        key_and_group = {key : list(group)}
        sub_data = []
        for item in key_and_group[key]:
            sub_data.append({
                "matnr": item.matnr,
                "quantity": item.quantity,
                "tp": item.tp,
                "vat": item.vat,
                "net_val": item.net_val,
                "batch": item.batch,
                "material_name": item.material_name,
                "brand_description": item.brand_description,
                "brand_name": item.brand_name,
                "received_quantity": item.received_quantity,
                "received_net_val": item.received_net_val,
            })
        main_data = {
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
            "cash_collection": key_and_group[key][0].cash_collection,
            "collection_status": key_and_group[key][0].collection_status,
            "gate_pass_no": key_and_group[key][0].gate_pass_no,
            "vehicle_no": key_and_group[key][0].vehicle_no,
            "product_list": sub_data
        }
        data.append(main_data)
    return Response({"success": True, "result": data}, status=status.HTTP_200_OK)

@api_view(['POST'])
def delivery_save(request):
    if request.method == 'POST':
        tz_Dhaka = pytz.timezone('Asia/Dhaka')
        serializer = DeliverySerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['received_date_time'] = datetime.now(tz_Dhaka)
            serializer.save()
            return Response({"success": True, "result": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)