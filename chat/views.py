from django.shortcuts import render


def chat_rooms(request):
    rooms = Room.objects.all()
    return render(request, "chat/chat_room_selector.html", {"rooms": rooms})
