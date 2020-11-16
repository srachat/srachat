from rest_framework import serializers

from .createupdatemodelserializer import CreateUpdateModelSerializer
from ..models.comment import Comment


class CreateUpdateCommentSerializer(CreateUpdateModelSerializer):

    class Meta:
        model = Comment
        fields = Comment.MODIFIABLE_FIELDS


class UpdateCommentSerializer(CreateUpdateCommentSerializer):
    """Empty now, but can be expanded later"""
    pass


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class SingleRoomCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        exclude = ['room']
