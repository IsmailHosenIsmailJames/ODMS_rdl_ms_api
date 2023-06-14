from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from collection_app.models import CashCollectionInfoModel
from itertools import groupby
import pytz
from delivery_app.models import DeliveryModel
from delivery_app.serializers import DeliverySerializer
from datetime import datetime

@api_view(['GET'])
def cash_collection_list(request,sap_id):
    if request.method == 'GET':
        d_type = request.query_params.get("type")
        query = " AND d.delivery_status = 'Done' "
        if d_type == 'All':
            query = query
        elif d_type == 'Remaining':
            query = query + "AND d.cash_collection_status IS NULL"
        else:
            query = query + "AND d.cash_collection_status = '"+d_type+"'"

        sql = "SELECT dis.*,rs.description route_name, " \
                "sis.billing_type,sis.partner,sis.matnr,sis.quantity,sis.tp,sis.vat,sis.net_val,sis.assigment,sis.gate_pass_no,sis.batch,sis.plant,sis.team,sis.created_on, " \
                "m.material_name,m.brand_description,m.brand_name, " \
                "CONCAT(c.name1,c.name2) customer_name,CONCAT(c.street,c.street1,c.street2) customer_address,c.mobile_no customer_mobile, " \
                "cl.latitude,cl.longitude, " \
                "dl.delivery_quantity,dl.delivery_net_val,IF(d.delivery_status IS NULL,'Pending',d.delivery_status) delivery_status,d.cash_collection,IF(d.cash_collection_status IS NULL,'Pending',d.cash_collection_status) cash_collection_status " \
                "FROM rdl_delivery_info_sap dis " \
                "INNER JOIN rdl_route_sap rs ON dis.route=rs.route " \
                "INNER JOIN rpl_sales_info_sap sis ON dis.billing_doc_no=sis.billing_doc_no " \
                "INNER JOIN rpl_material m ON sis.matnr=m.matnr " \
                "INNER JOIN rpl_customer c ON sis.partner=c.partner " \
                "LEFT JOIN exf_customer_location cl ON sis.partner=cl.customer_id " \
                "LEFT JOIN rdl_delivery d ON sis.billing_doc_no=d.billing_doc_no " \
                "LEFT JOIN rdl_delivery_list dl ON d.id=dl.delivery_id AND sis.matnr=dl.matnr " \
                "WHERE dis.billing_date = CURRENT_DATE() AND dis.da_code = '%s' "+query+" ;"

        data_list = CashCollectionInfoModel.objects.raw(sql,[sap_id])
        an_iterator = groupby(data_list, lambda x : x.id)
        data = []
        for key, group in an_iterator:
            key_and_group = {key : list(group)}
            sub_data = []
            for item in key_and_group[key]:
                sub_data.append({
                    "product_code": item.product_code,
                    "product_name": item.product_name,
                    "qty": item.qty,
                    "per_price": item.per_price,
                    "total_price": item.total_price,
                })

            main_data = {
                "id": key_and_group[key][0].id,
                "invoice_date": key_and_group[key][0].invoice_date,
                "customer_name": key_and_group[key][0].customer_name,
                "customer_addreess": key_and_group[key][0].customer_address,
                "customer_mobile": key_and_group[key][0].customer_mobile,
                "delevery_type": key_and_group[key][0].delevery_type,
                "route_name": key_and_group[key][0].route_name,
                "latitude": key_and_group[key][0].latitude,
                "longitude": key_and_group[key][0].longitude,
                "status": key_and_group[key][0].status,
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
        
        if request.data.get('type') == "cash_collection":
            serializer.validated_data['cash_collection_date_time'] = datetime.now(tz_Dhaka)
        elif request.data.get('type') == "return":
            serializer.validated_data['return_date_time'] = datetime.now(tz_Dhaka)
        
        serializer.update(delivery, serializer.validated_data)
        
        return Response({"success": True, "result": serializer.data}, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)