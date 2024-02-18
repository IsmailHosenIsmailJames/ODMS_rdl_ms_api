from django.urls import path
from attendance_app import views

urlpatterns = [
    path('start_work', views.attendance_start_work),
    path('end_work/<str:sap_id>', views.attendance_end_work),
    path('admin/attendance/list', views.admin_attendance_list),
]