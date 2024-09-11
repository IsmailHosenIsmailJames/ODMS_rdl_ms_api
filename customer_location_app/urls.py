from django.urls import path
from customer_location_app import views

urlpatterns = [
    path('list', views.customer_list),
    path('details/<int:partner>', views.customer_details),
]