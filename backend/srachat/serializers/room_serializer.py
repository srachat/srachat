from typing import List

from rest_framework import serializers

from .create_update_model_serializer import CreateUpdateModelSerializer
from ..models.room import Room
from ..models.tag import Tag


class CreateUpdateRoomSerializer(CreateUpdateModelSerializer):
    # TODO: add validation that creator cannot be banned
    class Meta:
        model = Room
        fields = Room.MODIFIABLE_FIELD

    def validate_tags(self, value: List[Tag]):
        if len(value) > Room.TAGS_AMOUNT:
            raise serializers.ValidationError(f"Maximum amount of tags can be: {Room.TAGS_AMOUNT}")
        return value


class CreateRoomSerializer(CreateUpdateRoomSerializer):
    def save(self, **kwargs):
        # Overwritten to implicitly add a creator as one of the admins

        # Check that creator should always be specified in the view
        if "creator" not in kwargs:
            # This should not happen
            raise serializers.ValidationError("Creator should be specified as an argument for room creation")
        creator = kwargs["creator"]

        # Check if admins were specified
        admins = self.validated_data.get("admins", [])
        if not admins:
            admins = [creator]
        elif creator not in admins:
            admins.append(creator)
        return super().save(creator=creator, admins=admins)


class UpdateRoomSerializer(CreateUpdateRoomSerializer):
    """Empty now, but can be expanded later"""
    pass


class DetailListRoomSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = '__all__'

    def get_tags(self, obj):
        return Tag.get_names_by_ids(obj.tags.all())
