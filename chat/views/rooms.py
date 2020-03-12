from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from chat.models import Comment, Room
from chat.serializers.comment_serializer import SingleRoomCommentSerializer
from chat.serializers.room_serializer import RoomSerializer


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    @action(detail=True)
    def comments(self, request, pk=None, format=None):
        comments = Comment.objects.filter(room=pk)
        serializer = SingleRoomCommentSerializer(comments, many=True)
        return Response(serializer.data)

    @comments.mapping.post
    def add_comment(self, request, pk=None):
        serializer = SingleRoomCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(room=self.get_object())
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
