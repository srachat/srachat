from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404


class ChatUser(models.Model):
    image = models.ImageField(upload_to='images', null=True, blank=True)
    rooms = models.ManyToManyField("Room", blank=True, related_name='chat_users')
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
