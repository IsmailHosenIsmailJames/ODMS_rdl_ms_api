from django.urls import path
from delivery_app import views

urlpatterns = [
    path('list/<int:sap_id>', views.delivery_list),
]