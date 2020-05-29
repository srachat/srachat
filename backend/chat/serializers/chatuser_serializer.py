from rest_framework import serializers
from chat.models import ChatUser


class ChatUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    last_login = serializers.CharField(source='user.last_login', read_only=True)
    date_joined = serializers.CharField(source='user.date_joined', read_only=True)

    def update(self, instance, validated_data):
        user_data = validated_data.get('user', {})
        image_data = validated_data.get('image', instance.image)

        instance.user.username = user_data.get("username", instance.user.username)
        instance.user.first_name = user_data.get("first_name", instance.user.first_name)
        instance.user.last_name = user_data.get("last_name", instance.user.last_name)
        instance.image = image_data

        instance.user.save()
        instance.save()

        return instance

    class Meta:
        model = ChatUser
        exclude = ('user',)
