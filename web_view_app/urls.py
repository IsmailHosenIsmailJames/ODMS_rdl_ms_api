from django.urls import path
from . import views

urlpatterns = [
    path('summary/<int:da_code>', views.summary, name='da_summary'),
    path('export_pdf/<int:da_code>', views.da_summary_pdf, name='export_pdf'),
    path('test/<int:da_code>', views.test, name='test'),
]