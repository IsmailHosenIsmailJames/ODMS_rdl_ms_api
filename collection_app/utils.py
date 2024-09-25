import datetime
import pytz
from .models import PaymentHistory

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