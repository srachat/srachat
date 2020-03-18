from django.shortcuts import get_object_or_404
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
        comments = Comment.objects.filter(room=pk)
        serializer = SingleRoomCommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        serializer = SingleRoomCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(room=Room.objects.get(pk=pk))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetail(APIView):
    """
    This view is able to display, update and delete a single comment.
    If no room is specified in the url path, it should be given inside request body.
    """
    def get_comment(self, pk):
        return get_object_or_404(Comment, pk=pk)

    def get(self, request, room_pk, comment_pk, format=None):
        comment = self.get_comment(comment_pk)
        serializer = SingleRoomCommentSerializer(comment)
        return Response(serializer.data)

    def put(self, request, room_pk, comment_pk, format=None):
        comment = self.get_comment(comment_pk)
        serializer = SingleRoomCommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, room_pk, comment_pk, format=None):
        comment = self.get_comment(comment_pk)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
