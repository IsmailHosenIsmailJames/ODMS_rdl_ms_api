from rest_framework import serializers
from customer_location_app.models import CustomerLocationModel

class CustomerLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerLocationModel
        fields = ['work_area_t', 'customer_id', 'latitude', 'longitude']