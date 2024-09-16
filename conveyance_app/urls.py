from django.urls import path
from .views import TransportModeListView, ConveyanceListView, StartJourneyView, EndJourneyView

urlpatterns = [
    path('list', ConveyanceListView.as_view(), name='conveyance_list'),
    path('start', StartJourneyView.as_view(), name='start_journey'),
    path('end/<int:id>', EndJourneyView.as_view(), name='end_journey'),
    path('transport_modes', TransportModeListView.as_view(), name='transport_mode_list'),
]