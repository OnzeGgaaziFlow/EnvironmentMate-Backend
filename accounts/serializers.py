from django.db.models.base import Model
from accounts.models import User, Profile
from rest_framework import serializers


class CustomUserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class SignUpRequestDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"


class SignupRequestAcceptSerailizer(serializers.Serializer):
    class Meta:
        model = User
        fields = "__all__"
