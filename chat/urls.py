from django.urls import path

from chat import views

urlpatterns = [
    path('', views.chat_rooms, name="chat-rooms-page"),
]
