from rest_framework import serializers

from ..models.room import Room


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

    def validate_tags(self, value):
        if len(value) > Room.TAGS_AMOUNT:
            raise serializers.ValidationError(f"Maximum amount of tags can be: {Room.TAGS_AMOUNT}")
        return value
