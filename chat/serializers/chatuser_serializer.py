from django.contrib.auth.models import User
from rest_framework import serializers
from chat.models import ChatUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("last_login", "username", "first_name", "last_name", "date_joined")


class ChatUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ChatUser
        fields = '__all__'
