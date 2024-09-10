from django.urls import path
from pharmaceuticals_location import views

urlpatterns = [
    path('save/', views.save_pharmaceuticals_location)
]