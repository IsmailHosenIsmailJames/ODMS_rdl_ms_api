from django.urls import path
from customer_location_app import views
from .views import update_or_insert_customer_location

urlpatterns = [
    path('list/<int:da_code>', views.customer_list),
    path('v2/list/<int:da_code>', views.customer_list_v2),
    path('details/<int:partner>', views.customer_details),
    path('customer_location_update', update_or_insert_customer_location, name='update_or_insert_customer_location'),
]