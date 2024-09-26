import datetime
import pytz
from .models import PaymentHistory
from delivery_app.models import DeliveryInfoModel


def get_da_route(da_code):
    sql="SELECT billing_doc_no,route FROM rdl_delivery_info_sap WHERE da_code='%s' ORDER BY billing_date DESC LIMIT 1"
    data=DeliveryInfoModel.objects.raw(sql,[da_code])
    data_list=list(data)
    if data_list:
        route = data_list[0].route
        return route
    return None

def CreatePaymentHistoryObject(billing_doc_no,partner,da_code,route_code,cash_collection,cash_collection_date_time,cash_collection_latitude,cash_collection_longitude):
    PaymentHistory.objects.create(
        billing_doc_no=billing_doc_no,
        partner=partner, 
        da_code=da_code,
        route_code=route_code,
        cash_collection=cash_collection,
        cash_collection_date_time=cash_collection_date_time,
        cash_collection_latitude=cash_collection_latitude,
        cash_collection_longitude=cash_collection_longitude
    )