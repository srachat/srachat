from django.conf import settings
from django.db import models
from django.utils import timezone


class Room(models.Model):
    title = models.CharField(max_length=250)

    def __str__(self):
        return self.title


class Comment(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE,
                             related_name='comments')
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return self.body
