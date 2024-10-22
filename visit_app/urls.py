from django.urls import path 
from .views import *

urlpatterns = [
    path('create',VisitHistoryCreateView.as_view(),name="create_visit_history"),
    path('visit_type',VisitTypeView.as_view(),name="visit_type"),
]
