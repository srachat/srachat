from rest_framework import serializers
from ..models.comment import Comment
from ..models.room import Room


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class SingleRoomCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        exclude = ['room']


def _save(self, **kwargs):
    _class = self.__class__
    # Argument in kwargs has a higher priority than the class attribute
    room = kwargs.pop("room", None) or _class.room
    if room is None:
        raise ValueError("room should be either specified as a class or method attribute.")
    super(_class, self).save(room=room, **kwargs)


class BoundRoomCommentSerializer:
    def __init__(self, room: Room):
        self.room = room

        self.serializer_class = SingleRoomCommentSerializer
        self.serializer_class.room = room
        self.serializer_class.save = _save

    def __call__(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)

