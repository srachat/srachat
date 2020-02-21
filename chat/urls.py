from django.urls import path

from chat import views

urlpatterns = [
    path('chat_rooms', views.chat_rooms, name="chat-rooms-page"),
]
