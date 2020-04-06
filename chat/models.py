from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404


class Room(models.Model):
    creator = models.ForeignKey("ChatUser", null=True, on_delete=models.CASCADE, related_name="created_room")
    title = models.CharField(max_length=250, unique=True)

    @staticmethod
    def get_room_or_404(pk):
        return get_object_or_404(Room, pk=pk)

    def __str__(self):
        return self.title


class Comment(models.Model):
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey("ChatUser", null=True, on_delete=models.CASCADE, related_name="created_comment")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='comments')

    class Meta:
        ordering = ('created',)

    @staticmethod
    def get_comment_or_404(pk):
        return get_object_or_404(Comment, pk=pk)

    def __str__(self):
        return self.body


class ChatUser(models.Model):
    rooms = models.ManyToManyField(Room, related_name='chat_users', blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images', null=True, blank=True)

    @staticmethod
    def get_chat_user_or_404(pk):
        return get_object_or_404(ChatUser, pk=pk)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        ChatUser.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.chatuser.save()
