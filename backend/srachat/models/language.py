from django.db import models
from django.utils.translation import gettext_lazy as _


class LanguageChoices(models.TextChoices):
    ENGLISH = "EN", _("English")
    GERMAN = "GE", _("German")
    RUSSIAN = "RU", _("Russian")
