from rest_framework import generics, status, parsers
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models.team_number import TeamNumber
from ..models.user import ChatUser, Participation
from ..models.room import Room
from ..permissions import IsAccountOwnerOrReadOnly, IsRoomAdminOrReadOnly
from ..serializers.chatuser_serializer import ChatUserSerializer
from ..serializers.participation_serializer import ParticipationSerializer
from ..validators import int_validator


class ChatUserList(generics.ListAPIView):
    """
    This view is able to display all existing users.
    """
    queryset = ChatUser.objects.filter(user__is_staff=False)
    serializer_class = ChatUserSerializer


class ChatUserDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    This view is able to display or update the user data.
    """
    permission_classes = [IsAuthenticatedOrReadOnly & IsAccountOwnerOrReadOnly]
    parser_classes = [parsers.MultiPartParser]
    queryset = ChatUser.objects.filter(user__is_staff=False)
    serializer_class = ChatUserSerializer


class RoomUserList(APIView):
    """
    Returns all users of a room, adds a new one or deletes a caller of the endpoint.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, pk, format=None):
        room = Room.get_room_or_404(pk)
        chat_user_ids = ChatUser.objects.filter(rooms=room).values_list('id', flat=True)
        return Response(chat_user_ids)

    def post(self, request, pk):
        room = Room.get_room_or_404(pk)
        if not room.is_active:
            return Response(
                "You cannot become a participant in an inactive room",
                status=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS
            )

        user = ChatUser.objects.get(user=request.user)
        if user in room.banned_users.all():
            return Response("You are banned in this room", status=status.HTTP_403_FORBIDDEN)

        team_number = TeamNumber.get_team_number_from_data(request.data)

        amount_of_participants = Participation.objects.filter(room=room, team_number=team_number).count()
        if amount_of_participants >= room.max_participants_in_team:
            return Response("This team reached maximum amount of participants", status=status.HTTP_406_NOT_ACCEPTABLE)

        serializer = ParticipationSerializer(data=dict(chatuser=user.id, room=room.id, team_number=team_number))
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_202_ACCEPTED)

    def delete(self, request, pk):
        room = Room.get_room_or_404(pk)
        chat_user = ChatUser.objects.get(user=request.user)
        room.chat_users.remove(chat_user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoomBannedUserList(APIView):
    """
    Bans a user or retrieves all banned user for a specified room
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def check_permission_to_ban(self, request, room):
        if not IsRoomAdminOrReadOnly().has_object_permission(request, self, room):
            return Response("Only admin can add users to a block list", status=status.HTTP_403_FORBIDDEN)

    def validate_and_return_room_and_user_id(self, request, pk):
        room = Room.get_room_or_404(pk)
        self.check_permission_to_ban(request, room)
        if "id" not in request.data:
            raise ValidationError(detail="Id must be provided", code=400)
        user_id = int_validator(request.data["id"])
        return room, user_id

    def get(self, request, pk, format=None):
        room = Room.get_room_or_404(pk)
        banned_user_ids = room.banned_users.values_list('id', flat=True)
        return Response(banned_user_ids)

    def post(self, request, pk):
        room, user_id = self.validate_and_return_room_and_user_id(request, pk)
        if user_id in room.admins.values_list("id", flat=True) or user_id == room.creator.id:
            return Response("Admins or a creator cannot be banned", status=status.HTTP_409_CONFLICT)
        room.chat_users.remove(user_id)
        room.banned_users.add(ChatUser.get_chat_user_or_404(user_id))
        return Response(status=status.HTTP_202_ACCEPTED)

    def delete(self, request, pk):
        room, user_id = self.validate_and_return_room_and_user_id(request, pk)
        if user_id in room.banned_users.values_list("id", flat=True):
            room.banned_users.remove(user_id)
        else:
            return Response("Chat user is not blocked for this room", status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
