from rest_framework import serializers
from .models import UserList

class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserList
        exclude = ('password',)

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserList
        fields = ['sap_id', 'full_name', 'mobile_number','user_type','password']
