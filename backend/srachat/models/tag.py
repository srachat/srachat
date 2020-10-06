from django.db import models
from django.shortcuts import get_object_or_404


class Tag(models.Model):
    AMOUNT = 4
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


