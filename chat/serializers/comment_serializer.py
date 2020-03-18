from rest_framework import serializers
from chat.models import Comment


class SingleRoomCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        exclude = ['room']
