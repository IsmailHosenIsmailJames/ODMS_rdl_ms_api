from rest_framework import serializers
from delivery_app.models import DeliveryModel,DeliveryListModel


class DeliveryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryListModel
        fields = "__all__"
        read_only_fields = ("delivery", )

class DeliverySerializer(serializers.ModelSerializer):
    deliverys = DeliveryListSerializer(many=True)

    class Meta:
        model = DeliveryModel
        fields = "__all__"

    def create(self, validated_data):
        deliverys_data = validated_data.pop('deliverys')
        delivery = DeliveryModel.objects.create(**validated_data)
        for delivery_data in deliverys_data:
            DeliveryListModel.objects.create(delivery=delivery, **delivery_data)
        return delivery