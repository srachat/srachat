from django.shortcuts import render

from chat.forms import RoomForm
from chat.models import Room


def chat_rooms(request):
    if request.method == "POST":
        room_form = RoomForm(request.POST)
        if room_form.is_valid():
            room_form.save()
    else:
        room_form = RoomForm()
    rooms = Room.objects.all()
    return render(
        request, "chat/chat_room_selector.html",
        {
            "chat_rooms": rooms,
            "room_form": room_form
        }
    )
