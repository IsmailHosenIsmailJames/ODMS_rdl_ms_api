from django.urls import path
from user_app import views

urlpatterns = [
    path('user_login', views.user_login),
    path('user_registration', views.user_registration),
]