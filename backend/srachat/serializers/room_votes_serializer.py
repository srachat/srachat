from rest_framework import serializers

from ..models.room import RoomVote


class RoomVotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomVote
        fields = '__all__'
