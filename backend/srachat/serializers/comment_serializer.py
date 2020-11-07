from rest_framework import serializers
from ..models.comment import Comment


class CreateUpdateCommentSerializer(serializers.ModelSerializer):
    # TODO: add validation that creator cannot be banned
    class Meta:
        model = Comment
        fields = Comment.MODIFIABLE_FIELD

    def is_valid(self, raise_exception=False):
        if hasattr(self, 'initial_data'):
            payload_keys = self.initial_data.keys()
            serializer_fields = self.fields.keys()
            extra_fields = list(filter(lambda key: key not in serializer_fields, payload_keys))
            if extra_fields:
                raise serializers.ValidationError(f"Extra fields {extra_fields} in payload")
        return super().is_valid(raise_exception)


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
