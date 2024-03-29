from rest_framework import status, generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .modeldetail import ModelDetailView
from ..models.comment import Comment
from ..models.room import Room
from ..models.user import ChatUser, Participation
from ..permissions import IsCreatorOrReadOnly, IsRoomParticipantOrReadOnly, IsAllowedRoomOrReadOnly
from ..serializers.comment_serializer import ListCommentSerializer, SingleRoomCommentSerializer, UpdateCommentSerializer


class CommentList(generics.GenericAPIView):
    """
    This view is able to display or add comments in all srachat rooms
    or if the room id is given to display or add comments to the given room.
    """
    permission_classes = [IsAuthenticatedOrReadOnly & IsRoomParticipantOrReadOnly & IsAllowedRoomOrReadOnly]
    queryset = Room.objects.all()
    serializer_class = SingleRoomCommentSerializer

    def get(self, request, pk, format=None):
        room = self.get_object()
        comments = Comment.objects.filter(room=room)
        serializer = SingleRoomCommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        room = self.get_object()
        if not room.is_active:
            return Response(
                "You cannot leave a comment in an inactive room",
                status=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS
            )

        comment_creator = ChatUser.objects.get(user=request.user)
        comment_body = request.data.get("body", "")
        if not comment_body:
            raise ValidationError("You have to specify the comment body and it cannot be empty.")

        data = {
            "body": comment_body,
            "creator": comment_creator.id,
            "team_number": Participation.objects.get(chatuser=comment_creator, room=room).team_number
        }
        serializer = SingleRoomCommentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(room=room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentDetail(ModelDetailView):
    """
        This view is able to display, update and delete a single comment.
    """
    permission_classes = [IsAuthenticatedOrReadOnly & IsCreatorOrReadOnly & IsAllowedRoomOrReadOnly]
    queryset = Comment.objects.all()

    update_serializer_class = UpdateCommentSerializer
    detail_serializer_class = ListCommentSerializer
