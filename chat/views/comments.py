from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import Comment, Room
from chat.serializers.comment_serializer import SingleRoomCommentSerializer


class CommentList(APIView):
    """
    This view is able to display or add comments in all chat rooms
    or if the room id is given to display or add comments to the given room.
    """
    def get(self, request, pk, format=None):
        room = Room.get_room_or_404(pk)
        comments = Comment.objects.filter(room=room)
        serializer = SingleRoomCommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        room = Room.get_room_or_404(pk)
        serializer = SingleRoomCommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(room=room)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentDetail(APIView):
    """
    This view is able to display, update and delete a single comment.
    If no room is specified in the url path, it should be given inside request body.
    """
    def get(self, request, room_pk, comment_pk, format=None):
        room = Room.get_room_or_404(room_pk)
        comment = Comment.get_comment_or_404(comment_pk)
        serializer = SingleRoomCommentSerializer(comment)
        return Response(serializer.data)

    def put(self, request, room_pk, comment_pk, format=None):
        room = Room.get_room_or_404(room_pk)
        comment = Comment.get_comment_or_404(comment_pk)
        serializer = SingleRoomCommentSerializer(comment, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    def delete(self, request, room_pk, comment_pk):
        room = Room.get_room_or_404(room_pk)
        comment = Comment.get_comment_or_404(comment_pk)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
