from django.db import models
from django.shortcuts import get_object_or_404


class Comment(models.Model):
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(
        "ChatUser", null=True, on_delete=models.CASCADE, related_name="created_comment"
    )
    room = models.ForeignKey("Room", on_delete=models.CASCADE, related_name='comments')

    class Meta:
        ordering = ('created',)

    @staticmethod
    def get_comment_or_404(pk):
        return get_object_or_404(Comment, pk=pk)

    def __str__(self):
        return self.body
