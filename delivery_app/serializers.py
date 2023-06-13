from rest_framework import serializers
from delivery_app.models import DeliveryModel,DeliveryListModel


class DeliveryListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    
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
    
    
    def update(self, instance, validated_data):
        deliverys_data = validated_data.pop('deliverys')

        # Update delivery list items
        print(deliverys_data)
        for delivery_data in deliverys_data:
            delivery_list_id = delivery_data.get('id')
            print(delivery_list_id)
            if delivery_list_id:
                try:
                    delivery_list_item = DeliveryListModel.objects.get(delivery=instance, id=delivery_list_id)
                    for attr, value in delivery_data.items():
                        setattr(delivery_list_item, attr, value)
                    delivery_list_item.save()
                except DeliveryListModel.DoesNotExist:
                    pass

        # Update delivery instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance