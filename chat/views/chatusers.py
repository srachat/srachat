from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import ChatUser, Room
from chat.serializers.chatuser_serializer import ChatUserSerializer


class ChatUserList(generics.ListCreateAPIView):
    """
    This view is able to display all existing rooms
    or to create a new one.
    """
    queryset = ChatUser.objects.all()
    serializer_class = ChatUserSerializer


class ChatUserDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    This view is able to display all existing rooms
    or to create a new one.
    """
    queryset = ChatUser.objects.all()
    serializer_class = ChatUserSerializer


class RoomUserList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, pk, format=None):
        room = Room.get_room_or_404(pk)
        chat_user_ids = ChatUser.objects.filter(rooms=room).values_list('id', flat=True)
        return Response(chat_user_ids)

    def post(self, request, pk):
        room = Room.get_room_or_404(pk)
        chat_user = ChatUser.objects.get(user=request.user)
        chat_users_amount = ChatUser.objects.filter(rooms=pk).count()
        chat_user_rooms_amount = Room.objects.filter(chat_users=chat_user).count()
        if chat_users_amount > 0:
            return Response(
                "Your reached the limit of users for this room.",
                status=status.HTTP_426_UPGRADE_REQUIRED
            )
        if chat_user_rooms_amount > 0:
            return Response(
                "Your reached the limit of rooms for your user. Consider upgrading to better type.",
                status=status.HTTP_426_UPGRADE_REQUIRED
            )
        room.chat_users.add(chat_user)
        return Response(status=status.HTTP_202_ACCEPTED)

    def delete(self, request, pk):
        room = Room.get_room_or_404(pk)
        chat_user = ChatUser.objects.get(user=request.user)
        room.chat_users.remove(chat_user)
        return Response(status=status.HTTP_202_ACCEPTED)

