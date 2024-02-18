from django.urls import path
from user_app import views

urlpatterns = [
    path('admin_login', views.user_admin_login),
    path('user_login', views.user_login),
    path('user_details', views.user_details),
    path('user_registration', views.user_registration),
    path('user_list', views.user_list),
    path('admin/user/list', views.admin_user_list),
    path('admin/user/insert', views.admin_insert_user),
    path('admin/user/update', views.admin_update_user),
    path('admin/user/delete', views.admin_delete_user),
]