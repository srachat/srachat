from django.db import models
from django.shortcuts import get_object_or_404
from .tag import Tag


class Room(models.Model):
    TAGS_AMOUNT = 4

    creator = models.ForeignKey(
        "ChatUser", null=True, on_delete=models.CASCADE, related_name="created_room"
    )
    tags = models.ManyToManyField(Tag, related_name="rooms")
    title = models.CharField(max_length=250, unique=True)

    @staticmethod
    def get_room_or_404(pk):
        return get_object_or_404(Room, pk=pk)

    def __str__(self):
        return self.title
