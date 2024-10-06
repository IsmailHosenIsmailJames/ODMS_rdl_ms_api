import decimal
from operator import itemgetter
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from itertools import groupby
import pytz
from delivery_app.models import DeliveryInfoModel, DeliveryModel,DeliveryListModel
from delivery_app.serializers import DeliverySerializer
from datetime import datetime,timedelta
from django.db import connection
from django.utils import timezone
from .models import PaymentHistory, ReturnListModel
from decimal import Decimal
from . import utils
from .constants import tz_Dhaka

def execute_raw_query(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        results = cursor.fetchall()
    return results

@api_view(['GET'])
def cash_collection_list_v2(request,sap_id):
    if request.method == 'GET':
        d_type = request.query_params.get("type")
        date = request.query_params.get("date")
        query_date = " AND dis.billing_date = CURRENT_DATE() "
        if date != "":
            query_date = " AND dis.billing_date = '"+date+"' "
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
                "dl.return_quantity,dl.return_net_val,dl.delivery_quantity,dl.delivery_net_val,IF(d.delivery_status IS NULL,'Pending',d.delivery_status) delivery_status,d.cash_collection,IF(d.cash_collection_status IS NULL,'Pending',d.cash_collection_status) cash_collection_status , (SELECT SUM(d2.due_amount) FROM rdl_delivery d2 WHERE d.partner=sis.partner AND d2.billing_date<CURRENT_DATE) AS previous_due_amount " \
                "FROM rdl_delivery_info_sap dis " \
                "LEFT JOIN rdl_route_sap rs ON dis.route=rs.route " \
                "INNER JOIN rpl_sales_info_sap sis ON dis.billing_doc_no=sis.billing_doc_no " \
                "INNER JOIN rpl_material m ON sis.matnr=m.matnr " \
                "INNER JOIN rpl_customer c ON sis.partner=c.partner " \
                "LEFT JOIN (SELECT DISTINCT customer_id, latitude, longitude FROM rdl_customer_location LIMIT 1) cl ON sis.partner = cl.customer_id " \
                "LEFT JOIN rdl_delivery d ON sis.billing_doc_no=d.billing_doc_no " \
                "LEFT JOIN rdl_delivery_list dl ON d.id=dl.delivery_id AND sis.matnr=dl.matnr AND sis.batch=dl.batch " \
                "WHERE dis.da_code = '%s' "+query_date+query+" ;"
        
        data_list = DeliveryInfoModel.objects.raw(sql,[sap_id])
        if len(data_list) == 0:
            return Response({"success": False, "message": "Data not available!"}, status=status.HTTP_200_OK)
        else:
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
                    "previous_due_amount": key_and_group[key][0].previous_due_amount,
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
                        "gate_pass_no": group[0]['gate_pass_no'],
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
                "LEFT JOIN (SELECT DISTINCT customer_id, latitude, longitude FROM rdl_customer_location LIMIT 1) cl ON sis.partner = cl.customer_id" \
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
        sql = "SELECT sis.matnr,sis.batch,sis.vat,sis.quantity,sis.net_val,sis.tp FROM rpl_sales_info_sap sis WHERE sis.billing_doc_no = %s;"
        billing_doc_no = request.data.get('billing_doc_no')
        results = execute_raw_query(sql,[billing_doc_no])
        data=dict()
        total_net_val=0.00
        for result in results:
            matnr,batch,vat,quantity,net_val=result[0],result[1],float(result[2]),float(result[3]),float(result[4])
            total_net_val = total_net_val + vat + net_val
            unit_vat,unit_price= vat/quantity, net_val/quantity
            unit_total = unit_vat + unit_price
            key=str(str(matnr)+str(batch))
            data[key]={
                "matnr":matnr,
                "batch":batch,
                "vat":vat,
                "quantity":quantity,
                "net_val":net_val,
                "unit_vat":unit_vat,
                "unit_price":unit_price,
                "unit_total":unit_total
            }
            
        serializer.validated_data['net_val']=total_net_val
        
        if request.data.get('type') == "cash_collection":
            cash_collection = request.data.get('cash_collection')
            delivery_items=request.data.get('deliverys',[])
            return_amount=0.00
            for items in delivery_items:
                matnr=str(items['id'])
                batch=items['batch']
                return_quantity=float(items["return_quantity"])
                key=str(str(matnr)+str(batch))
                amount=data[key]["unit_total"]*return_quantity
                # amount=(data[matnr]['unit_vat']+data[matnr]['unit_price'])*items['return_quantity']
                if return_quantity>data[key]['quantity']:
                    return Response({"success":False,"message":"Return quantity exceeds total quantity"},status=status.HTTP_200_OK)
                return_amount+=amount
                if return_quantity>0:
                    try:
                        record=DeliveryListModel.objects.get(delivery=pk,matnr=matnr,batch=batch)
                        # calculate new return quantity
                        old_quantity=float(record.return_quantity)
                        new_quantity=return_quantity-old_quantity
                        # update record
                        record.return_quantity=return_quantity
                        record.return_net_val = data[key]["unit_total"]*return_quantity
                        record.delivery_quantity-=Decimal(new_quantity)
                        record.delivery_net_val-=Decimal(data[key]["unit_total"]*new_quantity)
                        record.save()
                        # print(new_quantity)
                        # if new_quantity>0:
                        #     utils.CreateReturnList(
                        #         matnr=matnr,
                        #         batch=batch,
                        #         return_quantity=new_quantity,
                        #         return_net_val=data[key]["unit_total"]*new_quantity,
                        #         billing_doc_no=billing_doc_no,
                        #         billing_date=request.data.get('billing_date'),
                        #         da_code=request.data.get('da_code'),
                        #         gate_pass_no=request.data.get('gate_pass_no'),
                        #         partner=request.data.get('partner'),
                        #         route_code=request.data.get('route_code'),
                        #         return_time=ReturnListModel.ReturnTime.v1
                        #     )
                    except DeliveryListModel.DoesNotExist:
                        return Response({"success":False,"message":"matnr does not found"},status=status.HTTP_200_OK)

            if return_amount>0.00:
                serializer.validated_data['return_status']=1
            serializer.validated_data['return_amount']=return_amount
            due = total_net_val - float(cash_collection)-return_amount
            serializer.validated_data['due_amount']=round(due, 2);
            serializer.validated_data['cash_collection_date_time'] = datetime.now(tz_Dhaka)
            # Create Payment History Object
            utils.CreatePaymentHistoryObject(
                billing_doc_no = billing_doc_no,
                partner = delivery.partner,
                da_code = delivery.da_code,
                route_code = delivery.route_code,
                cash_collection = cash_collection,
                cash_collection_date_time = datetime.now(tz_Dhaka),
                cash_collection_latitude = request.data.get('cash_collection_latitude', None),cash_collection_longitude = request.data.get('cash_collection_latitude', None)
                )
        
        elif request.data.get('type') == "return":
            serializer.validated_data['return_date_time'] = datetime.now(tz_Dhaka)
            
        serializer.update(delivery, serializer.validated_data)
        
        return Response({"success": True, "result": serializer.data}, status=status.HTTP_200_OK)
    print(serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def cash_overdue(request,da_code):
    if request.method == 'GET':
        route=utils.get_da_route(da_code)
        partner=request.query_params.get("partner")
        previous_date = timezone.now().date()-timedelta(days=1)

        sql = "SELECT dis.*,IFNULL(rs.description, 'No Route Name') AS route_name, " \
                "sis.billing_type,sis.partner,sis.matnr,sis.quantity,sis.tp,sis.vat,sis.net_val,sis.assigment,sis.gate_pass_no,sis.batch,sis.plant,sis.team,sis.created_on, " \
                "m.material_name,m.brand_description,m.brand_name, " \
                "CONCAT(c.name1,c.name2) customer_name,CONCAT(c.street,c.street1,c.street2) customer_address,c.mobile_no customer_mobile, " \
                "cl.latitude,cl.longitude, " \
                "d.id,dl.id list_id,d.transport_type," \
                "dl.return_quantity,dl.return_net_val,dl.delivery_quantity,dl.delivery_net_val,IF(d.delivery_status IS NULL,'Pending',d.delivery_status) delivery_status,d.cash_collection,d.due_amount,IF(d.cash_collection_status IS NULL,'Pending',d.cash_collection_status) cash_collection_status " \
                "FROM rdl_delivery_info_sap dis " \
                "LEFT JOIN rdl_route_sap rs ON dis.route=rs.route " \
                "INNER JOIN rpl_sales_info_sap sis ON dis.billing_doc_no=sis.billing_doc_no " \
                "INNER JOIN rpl_material m ON sis.matnr=m.matnr " \
                "INNER JOIN rpl_customer c ON sis.partner=c.partner " \
                "LEFT JOIN (SELECT DISTINCT customer_id, latitude, longitude FROM rdl_customer_location LIMIT 1) cl ON sis.partner = cl.customer_id " \
                "LEFT JOIN rdl_delivery d ON sis.billing_doc_no=d.billing_doc_no " \
                "LEFT JOIN rdl_delivery_list dl ON d.id=dl.delivery_id AND sis.matnr=dl.matnr AND sis.batch=dl.batch " \
                "WHERE d.route_code = %s AND d.due_amount != 0 AND d.billing_date < CURRENT_DATE "
        
        if partner:
            sql += f" AND d.partner={partner}"
        data_list = DeliveryInfoModel.objects.raw(sql,[route])
        print(sql)
        if len(data_list) == 0:
            return Response({"success": False, "message": "Data not available!"}, status=status.HTTP_200_OK)
        else:
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
                    "due_amount":key_and_group[key][0].due_amount,
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
                        "gate_pass_no": group[0]['gate_pass_no'],
                        "latitude": group[0]['latitude'],
                        "longitude": group[0]['longitude'],
                        "invoice_list": group,
                })

        return Response({"success": True, "result": customer_data}, status=status.HTTP_200_OK)
    
@api_view(['PUT'])
def collect_overdue(request):
    if request.method == 'PUT':
        data = request.data
        billing_doc_no=data.get('billing_doc_no')
        da_code=data.get('da_code')
        cash_collection = Decimal(str(data.get('cash_collection', '0')))
        cash_collection_latitude=data.get('cash_collection_latitude')
        cash_collection_longitude=data.get('cash_collection_longitude')
        print(cash_collection,billing_doc_no,da_code)
        try:
            delivery = DeliveryModel.objects.get(billing_doc_no=billing_doc_no)
        except DeliveryModel.DoesNotExist:
            return Response({"success":False,"message": "Delivery not found"}, status=status.HTTP_200_OK)
        if cash_collection>delivery.due_amount:
            return Response({"success":False,"message":"Cash collection exceed the due amount"}, status=status.HTTP_200_OK)
        # if delivery.due_amount:
        #     delivery.due_amount =Decimal('0.00') if delivery.due_amount-cash_collection<Decimal('0.00') else round(delivery.due_amount-cash_collection,2)
        delivery.due_amount =round(delivery.due_amount-cash_collection,2)
        delivery.cash_collection+=cash_collection
        delivery.save()
        utils.CreatePaymentHistoryObject(billing_doc_no=billing_doc_no,partner=delivery.partner,da_code=da_code,route_code=delivery.route_code,cash_collection=cash_collection,cash_collection_date_time=datetime.now(tz_Dhaka),cash_collection_latitude=cash_collection_latitude,cash_collection_longitude=cash_collection_longitude)
        return Response({"success": True,"message":"successfully collect overdue", "result":data}, status=status.HTTP_200_OK)
    return Response({"success":False,"message":'wrong method'},status=status.HTTP_200_OK)

@api_view(['GET'])
def monthly_report(request):
    if request.method=="GET":
        sql="SELECT billing_date,SUM(net_val) AS total_net_val,SUM(return_amount) AS total_return_amount,COUNT(CASE WHEN delivery_status = 'Done' THEN 1 END) AS total_complete_delivery,COUNT(billing_doc_no) AS total_delivery,COUNT(CASE WHEN cash_collection_status='Done' THEN 1 END) AS total_complete_collection,SUM(cash_collection) AS total_cash_collection FROM rdl_delivery WHERE MONTH(billing_date) = MONTH(CURRENT_DATE) AND YEAR(billing_date) = YEAR(CURRENT_DATE)GROUP BY billing_date ORDER BY billing_date ASC;"
        result = execute_raw_query(sql)
        if not result:
                return Response({"success": True, "result": []}, status=status.HTTP_200_OK)
        data_list = [
            {
                'billing_date': row[0],
                'total_net_val': row[1],
                'total_return_amount': row[2],
                'total_complete_delivery': row[3],
                'total_delivery': row[4],
                'total_complete_collection': row[5],
                'total_cash_collection': row[6],
            }
            for row in result
        ]
        # print(data_list)
        report=[]
        for row in data_list:
            date=str(row['billing_date'])
            total_net_val=float(row['total_net_val'])
            total_return_amount=float(row['total_return_amount'])
            revised_total_amount=total_net_val-total_return_amount
            total_delivery=float(row['total_delivery'])
            total_complete_delivery=float(row['total_complete_delivery'])
            total_complete_collection=float(row['total_complete_collection'])
            total_cash_collection=float(row['total_cash_collection'])
            print(date,revised_total_amount,total_delivery,total_complete_delivery,total_complete_collection,total_cash_collection)
            #calculation
            delivery_done=(total_complete_delivery/total_delivery)*100 if total_delivery>0 else 0
            collection_done=(total_complete_collection/total_delivery)*100 if total_delivery>0 else 0
            cash_collection=(total_cash_collection/revised_total_amount)*100 if revised_total_amount>0 else 0.00
            return_amount=(total_return_amount/total_net_val)*100 if total_net_val>0 else 0.00
            temp={
                "billing_date":date,
                "delivery_done":delivery_done,
                "collection_done":collection_done,
                "cash_collection":cash_collection,
                "return_amount":return_amount
            }
            report.append(temp)
            
        return Response({"success": True, "result": report},status=status.HTTP_200_OK)
    return Response({"success":False,"message":"wrong method"},status=status.HTTP_200_OK)