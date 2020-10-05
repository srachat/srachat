from django.contrib import admin

from .models.comment import Comment
from .models.room import Room
from .models.tag import Tag


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('body', 'room', 'created')
    list_filter = ('room',)
    search_fields = ('body',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('tag',)
    search_fields = ('tag',)
