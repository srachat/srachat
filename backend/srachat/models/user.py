from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404

from .team_number import TeamNumber


class Participation(models.Model):
    chatuser = models.ForeignKey("ChatUser", on_delete=models.CASCADE)
    room = models.ForeignKey("Room", on_delete=models.CASCADE)
    team_number = models.PositiveSmallIntegerField(choices=TeamNumber.choices)

    def save(self, *args, **kwargs):
        # TODO: optimize with indexing
        participants_in_team = Participation.objects.filter(room=self.room, team_number=self.team_number).count()
        if participants_in_team >= self.room.max_participants_in_team:
            raise OverflowError(f"Team number {self.team_number} is full.")
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ("chatuser", "room")


class ChatUser(models.Model):
    image = models.ImageField(upload_to='images', null=True, blank=True)
    rooms = models.ManyToManyField("Room", blank=True, related_name='chat_users', through=Participation)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    @staticmethod
    def get_chat_user_or_404(pk):
        return get_object_or_404(ChatUser, pk=pk)

    def __str__(self):
        return self.user.__str__()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        ChatUser.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.chatuser.save()
