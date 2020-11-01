from django.core.validators import MaxValueValidator
from django.db import models
from django.shortcuts import get_object_or_404
from .tag import Tag

from .language import LanguageChoices
from .team_number import TeamNumber


class Room(models.Model):
    """
    Main model for storing info about each chat room.
    # TODO: add more documentation
    """

    DEFAULT_MAX_PARTICIPANTS = 15
    POSSIBLE_MAX_PARTICIPANTS = 50
    TEAM_NAME_MAX_LENGTH = 30
    TITLE_MAX_LENGTH = 50
    TAGS_AMOUNT = 4

    # Parameters with different permissions on creation
    REQUIRED_FIELDS = ["tags", "title", "first_team_name", "second_team_name"]
    ALLOWED_TO_SPECIFY_FIELDS = ["admins", "language", "max_participants_in_team", "image"]

    MODIFIABLE_FIELD = REQUIRED_FIELDS + ALLOWED_TO_SPECIFY_FIELDS
    UNMODIFIABLE_FIELDS = ["banned_users", "created", "creator", "first_team_votes", "second_team_votes", "is_active"]

    # Parameters, which should be specified on creation
    tags = models.ManyToManyField(Tag, related_name="rooms")
    title = models.CharField(max_length=TITLE_MAX_LENGTH, unique=True)
    first_team_name = models.CharField(max_length=TEAM_NAME_MAX_LENGTH)
    second_team_name = models.CharField(max_length=TEAM_NAME_MAX_LENGTH)

    # Parameters, which can be filled automatically

    # Parameters, which are forbidden to be specified ...
    first_team_votes = models.PositiveSmallIntegerField(default=0)
    second_team_votes = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    # ... and even modified
    created = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey("ChatUser", null=True, on_delete=models.CASCADE, related_name="created_room")

    # Parameters, which may be specified
    # Admins should be filled with the same value as a creator
    admins = models.ManyToManyField("ChatUser", related_name="administrated_rooms", default=[])
    language = models.CharField(max_length=2, choices=LanguageChoices.choices, default=LanguageChoices.RUSSIAN)
    max_participants_in_team = models.PositiveSmallIntegerField(
        default=DEFAULT_MAX_PARTICIPANTS, validators=[MaxValueValidator(POSSIBLE_MAX_PARTICIPANTS)]
    )

    # Parameters, which may have blank values and can be specified on creation
    banned_users = models.ManyToManyField("ChatUser", related_name="forbidden_rooms", blank=True)
    image = models.ImageField(upload_to='images', null=True, blank=True)

    @staticmethod
    def get_room_or_404(pk):
        return get_object_or_404(Room, pk=pk)

    def __str__(self):
        return self.title


class RoomVote(models.Model):
    """
    TODO: add more documentation
    """
    room = models.ForeignKey("Room", on_delete=models.CASCADE)
    team_number = models.PositiveSmallIntegerField(choices=TeamNumber.choices + [(0, "Remove vote")])
    voter = models.ForeignKey("ChatUser", on_delete=models.CASCADE)

    # This one is added for possible statistics
    date_voted = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Voter: {self.voter}, Room: {self.room}, Team number: {self.team_number}, Voted: {self.date_voted}"

    class Meta:
        unique_together = ("voter", "room")
