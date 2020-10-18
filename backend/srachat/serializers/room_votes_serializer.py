from rest_framework import serializers

from ..models.room import RoomVotes


class RoomVotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomVotes
        fields = '__all__'
