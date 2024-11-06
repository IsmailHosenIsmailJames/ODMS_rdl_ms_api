from rest_framework import serializers
from .models import ConveyanceModel
from .models import TransportModeModel

class ConveyanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConveyanceModel
        fields = '__all__'

class TransportModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportModeModel
        fields = '__all__'