from django.urls import path
from customer_location_app import views
from .views import update_or_insert_customer_location

urlpatterns = [
    path('list', views.customer_list),
    path('details/<int:partner>', views.customer_details),
    path('customer_location/', update_or_insert_customer_location, name='update_or_insert_customer_location'),
]