from rest_framework import serializers
from .models import Room,CustomUser

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'name', 'dob', 'address', 'password']  
        extra_kwargs = {'password': {'write_only': True}} 

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data) 
        return user