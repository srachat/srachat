from django.shortcuts import render

from chat.forms import CommentForm, RoomForm
from chat.models import Comment, Room


def chat_rooms(request):
    if request.method == "POST":
        room_form = RoomForm(request.POST)
        if room_form.is_valid():
            room_form.save()
    room_form = RoomForm()
    rooms = Room.objects.all()
    return render(
        request, "chat/chat_room_selector.html",
        {
            "chat_rooms": rooms,
            "room_form": room_form
        }
    )


def single_chat_room(request, room_id):
    current_room = Room.objects.get(title=room_id)
    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        comment = comment_form.save(commit=False)
        comment.room = current_room
        comment.save()
    comment_form = CommentForm()
    current_room_comments = Comment.objects.filter(room = current_room)
    return render(
        request, "chat/single_chat_room.html",
        {
            "room_id": room_id,
            "comments": current_room_comments,
            "comment_form": comment_form
        }
    )
