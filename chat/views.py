from django.shortcuts import render

from .forms import RoomForm


def chat_rooms(request):
    if request.method == "POST":
        room_form = RoomForm(request.POST)
    else:
        room_form = RoomForm()
    rooms = Room.objects.all()
    return render(
        request, "chat/chat_room_selector.html",
        {
            "rooms": rooms,
            "room_form": room_form
        }
    )
