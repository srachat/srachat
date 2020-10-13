from rest_framework import generics

from ..models.tag import Tag
from ..serializers.tag_serializer import TagSerializer


class TagList(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
