from rest_framework import serializers
from .models import UserList,AdminUserList

class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserList
        exclude = ('password',)

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserList
        fields = ['sap_id', 'full_name', 'mobile_number','user_type','password']

class AdminUserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUserList
        exclude = ('password',)
