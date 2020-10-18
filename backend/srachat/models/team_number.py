from typing import Any, Dict

from django.db import models
from rest_framework.exceptions import ValidationError

from ..validators import int_validator


class TeamNumber(models.IntegerChoices):
    FIRST_TEAM = 1
    SECOND_TEAM = 2

    @staticmethod
    def get_team_number_from_data(data: Dict[str, Any]) -> int:
        if "team_number" not in data:
            raise ValidationError("You should specify a team number to join", code=400)
        team_number = int_validator(data["team_number"])
        return team_number
