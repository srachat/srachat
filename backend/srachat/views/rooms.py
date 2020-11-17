from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .modeldetail import ModelDetailView
from ..models.team_number import TeamNumber
from ..models.user import ChatUser, Participation
from ..models.room import Room, RoomVote
from ..permissions import IsCreatorOrReadOnly, IsRoomAdminOrReadOnly
from ..serializers.room_serializer import DetailListRoomSerializer, CreateRoomSerializer, UpdateRoomSerializer
from ..serializers.room_votes_serializer import RoomVotesSerializer


class RoomList(generics.CreateAPIView, generics.ListAPIView):
    """
    This view is able to display all existing rooms
    or to create a new one.
    # TODO: extend the documentation, describe the accepted parameters and behaviour
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = DetailListRoomSerializer

    def get_queryset(self):
        queryset = Room.objects.filter(is_active=True)
        filter_values = self.request.query_params.get("filter", None)
        if filter_values == "my":
            # TODO: refactor to use only filter argument without participation
            #   e.g. queryset.filter(participation__chatuser_id=self.request.user.id)
            participation = (Participation.objects
                             .filter(chatuser_id=self.request.user.id)
                             .values_list("room_id", flat=True))
            queryset = queryset.filter(id__in=participation)
        return queryset

    def post(self, request, *args, **kwargs):
        callee_user = ChatUser.objects.get(user=request.user)
        serializer = CreateRoomSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        room = serializer.save(creator=callee_user)
        headers = self.get_success_headers(serializer.data)
        return Response(room.id, status=status.HTTP_201_CREATED, headers=headers)


class RoomDetail(ModelDetailView):
    """
    This view is able to display, update and delete a single room.
    # TODO: extend the documentation. Describe all permissions.
    """
    permission_classes = [IsAuthenticatedOrReadOnly & (IsCreatorOrReadOnly | IsRoomAdminOrReadOnly)]
    queryset = Room.objects.all()

    update_serializer_class = UpdateRoomSerializer
    detail_serializer_class = DetailListRoomSerializer


class RoomVoteTeam(GenericAPIView):
    """
    View to let users vote for a team in a room

    As a body content this view takes `team_number` argument, which can be 0, 1, 2
    0 - revoke the vote
    1 - vote for the first team
    2 - vote for the second team

    If this is the first time user votes, they can only specify 1 or 2 team, since no vote can be revoked
    If user has already voted, 0 option can be specified as well, which would mean vote revoke

    Voting is saved to an intermediate model RoomVotes, which has a unique index user-room, which means
    that no user can have more than one vote
    Also this number is stored in the Room model as a plain positive integer number

    If a user decides to change their mind and vote for another team or to revoke a vote,
    RoomVotes object created is modified and remains the only one for a combination user-room

    # TODO: make a script, which would periodically clean RoomVotes objects with a 0 value,
        which in fact means no vote at all and can be safely removed
    # TODO: rewrite adding a vote to a room model as an action to a RoomVotes object
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Room.objects.all()

    @staticmethod
    def _handle_repeating_vote(team_number: int, room: Room, previously_voted_object: RoomVote):
        if team_number not in (0, 1, 2):
            raise ValidationError("You can choose either 1 or 2 to vote for a team, or 0 to revoke the vote")

        if previously_voted_object.team_number == 0:
            if team_number == 1:
                room.first_team_votes += 1
            elif team_number == 2:
                room.second_team_votes += 1
        elif previously_voted_object.team_number == 1:
            room.first_team_votes -= 1
            if team_number == 2:
                room.second_team_votes += 1
        elif previously_voted_object.team_number == 2:
            room.second_team_votes -= 1
            if team_number == 1:
                room.first_team_votes += 1
        room.save()
        previously_voted_object.team_number = team_number
        previously_voted_object.save()

    def post(self, request, pk):
        room = self.get_object()
        if not room.is_active:
            return Response("You cannot vote in an inactive room", status=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS)
        user = request.user

        team_number = TeamNumber.get_team_number_from_data(request.data)

        previously_voted = RoomVote.objects.filter(voter=ChatUser.objects.get(user=user), room=room)

        already_voted_for_team = previously_voted.filter(team_number=team_number).exists()
        if already_voted_for_team:
            return Response("You have already voted for this team", status=status.HTTP_406_NOT_ACCEPTABLE)

        previously_voted_object = previously_voted.first()
        if previously_voted.exists():
            RoomVoteTeam._handle_repeating_vote(team_number, room, previously_voted_object)
        else:
            serializer = RoomVotesSerializer(data=dict(voter=user.id, room=room.id, team_number=team_number))
            serializer.is_valid(raise_exception=True)
            if team_number == 1:
                room.first_team_votes += 1
            elif team_number == 2:
                room.second_team_votes += 1
            else:
                return Response(
                    "You are voting for the first time, specify the team",
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.save()
            room.save()

        return Response(status=status.HTTP_202_ACCEPTED)


class RoomDeactivate(GenericAPIView):
    """
    View to set the room into the deactivated state.
    Only a room creator can do that.
    """
    permission_classes = [IsAuthenticatedOrReadOnly & IsCreatorOrReadOnly]
    queryset = Room.objects.all()

    def post(self, request, pk):
        room = self.get_object()
        room.is_active = False
        room.save()
        return Response(status=status.HTTP_202_ACCEPTED)
