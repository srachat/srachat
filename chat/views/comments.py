from rest_framework import viewsets

from chat.models import Comment
from chat.serializers.comment_serializer import CommentSerializer


class CommentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
