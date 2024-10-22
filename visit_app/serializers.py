from rest_framework.serializers import ModelSerializer
from .models import VisitHistoryModel

class VisitHistorySerializer(ModelSerializer):
    class Meta:
        model = VisitHistoryModel
        fields = '__all__'