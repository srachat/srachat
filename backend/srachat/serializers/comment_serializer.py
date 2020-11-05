from rest_framework import serializers
from ..models.comment import Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('created', 'creator', 'room', 'team_number')


class SingleRoomCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        exclude = ['room']
