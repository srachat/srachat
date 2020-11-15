from channels.routing import URLRouter
from django.urls import re_path

from .consumers import RoomConsumer

srachat_router = URLRouter([
    re_path('^rooms/(?P<id>\w+)/$', RoomConsumer.as_asgi(), name="ws_room"),
])
