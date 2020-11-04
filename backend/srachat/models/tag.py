from typing import Iterable

from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    @staticmethod
    def get_names_by_ids(ids: Iterable[int]):
        return Tag.objects.filter(pk__in=ids).values_list("name", flat=True)
