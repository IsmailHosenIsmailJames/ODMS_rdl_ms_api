
from rest_framework import serializers
from .models import VisitHistoryModel

class VisitHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitHistoryModel
        fields = '__all__'   

class VisitTypeSerializer(serializers.Serializer):
    key = serializers.CharField()
    value = serializers.CharField()
       