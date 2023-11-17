from django.urls import path
from delivery_app import views

urlpatterns = [
    path('list/<int:sap_id>', views.delivery_list),
    path('v2/list/<int:sap_id>', views.delivery_list_v2),
    path('save', views.delivery_save),
]