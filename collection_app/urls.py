from django.urls import path
from collection_app import views

urlpatterns = [
    path('list/<int:sap_id>', views.cash_collection_list),
]