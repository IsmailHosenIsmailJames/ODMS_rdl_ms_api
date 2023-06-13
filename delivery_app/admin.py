from django.contrib import admin
from delivery_app.models import DeliveryModel, DeliveryListModel

class DeliveryAdminModel (admin.ModelAdmin):
    list_display=('id','billing_doc_no','billing_date','partner','da_code','route_code','transport_type','delivery_status','cash_collection','cash_collection_status')
    readonly_fields=('created_at','updated_at')
    search_fields = ('billing_doc_no','billing_date')
admin.site.register(DeliveryModel,DeliveryAdminModel)

class DeliveryListAdminModel (admin.ModelAdmin):
    list_display=('id','delivery','matnr','quantity','tp','vat','net_val','delivery_quantity','delivery_net_val')
    readonly_fields=('created_at','updated_at')
    search_fields = ('delivery.id','matnr')
admin.site.register(DeliveryListModel,DeliveryListAdminModel)