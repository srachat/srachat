from django.urls import path

from chat import views

urlpatterns = [
    path('', views.chat_rooms, name="chat-rooms-page"),
    path('<str:room_id>/', views.single_chat_room, name="single-chat-room"),
]
