from django.urls import path
from user_app import views

urlpatterns = [
    path('admin_login', views.user_admin_login),
    path('user_login', views.user_login),
    path('user_registration', views.user_registration),
]