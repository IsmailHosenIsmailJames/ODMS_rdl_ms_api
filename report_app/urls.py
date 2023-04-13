from django.urls import path
from report_app import views

urlpatterns = [
    path('dashboard/<int:sap_id>', views.dashboard_report),
]