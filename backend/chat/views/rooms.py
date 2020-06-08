from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from chat.models import Room, ChatUser
from chat.permissions import IsCreatorOrReadOnly
from chat.serializers.room_serializer import RoomSerializer


class RoomList(
    generics.CreateAPIView,
    generics.ListAPIView
):
    """
    This view is able to display all existing rooms
    or to create a new one.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(creator=ChatUser.objects.get(user=request.user))
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class RoomDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    This view is able to display, update and delete a single room.
    """
    permission_classes = [IsAuthenticatedOrReadOnly & IsCreatorOrReadOnly]
    queryset = Room.objects.all()
    serializer_class = RoomSerializer