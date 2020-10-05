from django.db import models
from django.shortcuts import get_object_or_404


class Tag(models.Model):
    name = models.CharField(max_length=50)

    @staticmethod
    def get_tag_room_or_404(pk):
        return get_object_or_404(Tag, pk=pk)

    def __str__(self):
        return self.name


