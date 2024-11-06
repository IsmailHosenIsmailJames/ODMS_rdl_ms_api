from django.urls import path
from . import views

urlpatterns = [
    path('summary/<int:da_code>', views.summary, name='da_summary'),
    path('export_pdf/<int:da_code>', views.da_summary_pdf, name='export_pdf'),
    path('test/<int:da_code>', views.test, name='test'),
    path('reports/<int:da_code>', views.reports, name='reports'),
    path('return_list/v1/<int:da_code>', views.product_return_list_v1, name='return_list_v1'),
    path('due_amount_list/<int:da_code>', views.due_amount_list, name='due_amount_list'),
    path('return_list/v2/<int:da_code>', views.product_return_list_v2, name='return_list_v2'),
    path('dashboard_manual', views.admin_dashboard_manual, name='dashboard_manual'),
    path('manual', views.dashboard_manual, name='manual'),
]