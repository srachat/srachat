from django.db import models
from django.shortcuts import get_object_or_404
from .tag import Tag

from .language import LanguageChoices
from .team_number import TeamNumber


class Room(models.Model):
    TEAM_NAME_MAX_LENGTH = 30
    TAGS_AMOUNT = 4

    # Primary parameters that should be filled
    admins = models.ManyToManyField("ChatUser", related_name="administrated_rooms", default=[])
    creator = models.ForeignKey(
        "ChatUser", null=True, on_delete=models.CASCADE, related_name="created_room"
    )
    tags = models.ManyToManyField(Tag, related_name="rooms")
    title = models.CharField(max_length=250, unique=True)

    # Team stuff
    first_team_name = models.CharField(max_length=TEAM_NAME_MAX_LENGTH)
    second_team_name = models.CharField(max_length=TEAM_NAME_MAX_LENGTH)
    first_team_votes = models.PositiveSmallIntegerField(default=0)
    second_team_votes = models.PositiveSmallIntegerField(default=0)

    # Parameters with default values
    created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    language = models.CharField(max_length=2, choices=LanguageChoices.choices, default=LanguageChoices.RUSSIAN)
    max_participants_in_team = models.PositiveSmallIntegerField(default=15)

    # Parameters, which may have blank values
    banned_users = models.ManyToManyField("ChatUser", related_name="forbidden_rooms", blank=True)
    image = models.ImageField(upload_to='images', null=True, blank=True)

    @staticmethod
    def get_room_or_404(pk):
        return get_object_or_404(Room, pk=pk)

    def __str__(self):
        return self.title


class RoomVotes(models.Model):
    room = models.ForeignKey("Room", on_delete=models.CASCADE)
    team_number = models.PositiveSmallIntegerField(choices=TeamNumber.choices + [(0, "Remove vote")])
    voter = models.ForeignKey("ChatUser", on_delete=models.CASCADE)

    # This one is added for possible statistics
    date_voted = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("voter", "room")
