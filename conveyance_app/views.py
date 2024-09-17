from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ConveyanceModel
from .models import TransportModeModel
from .serializers import ConveyanceSerializer
from .serializers import TransportModeSerializer
from django.utils import timezone
from django.db.models import Q

class TransportModeListView(APIView):
    def get(self, request, *args, **kwargs):
        # Retrieve distinct transport_mode values from the database
        transport_modes = TransportModeModel.objects.filter(
            Q(status=1)
        )
        serializer = TransportModeSerializer(transport_modes, many=True)
        return Response({"success": True, "result": serializer.data}, status=status.HTTP_200_OK)
    
# Conveyance List (Today or filter by date)
class ConveyanceListView(APIView):
    def get(self, request, *args, **kwargs):
        # Get the 'date' and 'da_code' from the query parameters
        date_filter = request.GET.get('date', timezone.now().date())
        da_code = request.GET.get('da_code')
        
        # Ensure da_code is provided, if not, return an error response
        if not da_code:
            return Response({"success": False, "message": "da_code is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Filter conveyances by date and da_code
        conveyances = ConveyanceModel.objects.filter(
            Q(start_journey_date_time__date=date_filter) & Q(da_code=da_code)
        )
        
        # Serialize the result
        serializer = ConveyanceSerializer(conveyances, many=True)
        
        return Response({"success": True, "result": serializer.data}, status=status.HTTP_200_OK)

# Start Journey
class StartJourneyView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        data['journey_status'] = 'live'
        data['start_journey_date_time'] = timezone.now()  # Auto set current time for start
        serializer = ConveyanceSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "result": serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False, "message": serializer.errors}, status=status.HTTP_200_OK)
    

# End Journey
class EndJourneyView(APIView):
    def put(self, request, id, *args, **kwargs):
        try:
            conveyance = ConveyanceModel.objects.get(id=id)
        except ConveyanceModel.DoesNotExist:
            return Response({"success": False, "message": "Journey not found"}, status=status.HTTP_200_OK)
        
        data = request.data
        conveyance.end_journey_longitude = data.get('end_journey_longitude')
        conveyance.end_journey_date_time = timezone.now()  # Auto set current time for end
        conveyance.transport_mode = data.get('transport_mode')
        conveyance.transport_cost = data.get('transport_cost')
        conveyance.journey_status = 'end'
        conveyance.save()

        serializer = ConveyanceSerializer(conveyance)
        return Response({"success": True, "result": serializer.data}, status=status.HTTP_200_OK)
