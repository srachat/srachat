from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from ..models.comment import Comment
from ..models.user import ChatUser
from ..models.room import Room
from ..permissions import IsCreatorOrReadOnly, IsRoomParticipantOrReadOnly
from ..serializers.comment_serializer import CommentSerializer, SingleRoomCommentSerializer


class CommentList(generics.GenericAPIView):
    """
    This view is able to display or add comments in all chat rooms
    or if the room id is given to display or add comments to the given room.
    """
    permission_classes = [IsAuthenticatedOrReadOnly & IsRoomParticipantOrReadOnly]
    queryset = Room.objects.all()
    serializer_class = CommentSerializer

    def get(self, request, pk, format=None):
        room = self.get_object()
        comments = Comment.objects.filter(room=room)
        serializer = SingleRoomCommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        room = self.get_object()
        serializer = SingleRoomCommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(room=room, creator=ChatUser.objects.get(user=request.user))
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    This view is able to display, update and delete a single comment.
    """
    permission_classes = [IsAuthenticatedOrReadOnly & IsCreatorOrReadOnly]
    queryset = Comment.objects.all()
    serializer_class = SingleRoomCommentSerializer
