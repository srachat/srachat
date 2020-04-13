from rest_framework import serializers
from chat.models import ChatUser


class ChatUserSerializer(serializers.ModelSerializer):
    last_login = serializers.CharField(source='user.last_login')
    username = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    date_joined = serializers.CharField(source='user.date_joined')

    class Meta:
        model = ChatUser
        fields = '__all__'
