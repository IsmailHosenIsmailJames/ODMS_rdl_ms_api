from django.urls import path
from collection_app import views

urlpatterns = [
    path('list/<int:sap_id>', views.cash_collection_list),
    path('v2/list/<int:sap_id>', views.cash_collection_list_v2),
    path('save/<str:pk>', views.cash_collection_save),
]