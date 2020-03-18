from rest_framework import viewsets, generics

from chat.models import Room
from chat.serializers.room_serializer import RoomSerializer


class RoomList(generics.ListCreateAPIView):
    """
    This view is able to display all existing rooms
    or to create a new one.
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class RoomDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    This view is able to display, update and delete a single room.
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
