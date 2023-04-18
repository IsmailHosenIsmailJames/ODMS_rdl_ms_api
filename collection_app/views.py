from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from collection_app.models import CashCollectionInfoModel
from itertools import groupby

@api_view(['GET'])
def cash_collection_list(request,sap_id):
    if request.method == 'GET':
        d_type = request.query_params.get("type")
        sql = "SELECT d.billing_doc_no id, d.billing_date invoice_date, " \
            "CONCAT(c.name1,c.name2) customer_name,CONCAT(c.street,c.street1,c.street2) customer_address,c.mobile_no customer_mobile, " \
            "d.transport_type delevery_type,rs.description route_name, cl.latitude, cl.longitude, 'Pending' status, " \
            "dl.matnr product_code, m.brand_description product_name, dl.quantity qty, dl.tp per_price, dl.net_val total_price " \
            "FROM rdl_delivery_list dl  " \
            "INNER JOIN rdl_delivery d ON dl.delivery_id=d.id  " \
            "INNER JOIN rpl_sales_info_sap sis On d.billing_doc_no=sis.billing_doc_no " \
            "INNER JOIN rpl_customer c ON d.partner=c.partner " \
            "INNER JOIN rdl_route_sap rs ON d.route_code=rs.route " \
            "LEFT JOIN exf_customer_location cl ON d.partner=cl.customer_id " \
            "INNER JOIN rpl_material m ON dl.matnr=m.matnr " \
            "WHERE d.delivery_status='Done' AND d.da_code='%s' GROUP BY sis.billing_doc_no,dl.matnr;"

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
