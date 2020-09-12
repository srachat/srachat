from django.contrib import admin

from .models import Room, Comment


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('body', 'room', 'created')
    list_filter = ('room',)
    search_fields = ('body',)
