from typing import Any, Dict

from django.db import models
from rest_framework.exceptions import ValidationError

from ..validators import validate_non_negative_int


class TeamNumber(models.IntegerChoices):
    FIRST_TEAM = 1
    SECOND_TEAM = 2

    @staticmethod
    def get_team_number_from_data(data: Dict[str, Any]) -> int:
        if "team_number" not in data:
            raise ValidationError("You should specify a team number to perform the action")
        team_number = validate_non_negative_int(data["team_number"])
        return team_number
