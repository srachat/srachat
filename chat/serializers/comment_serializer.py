from rest_framework import serializers
from chat.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class SingleRoomCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["body", "created"]
