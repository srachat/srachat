from channels.routing import URLRouter
from django.urls import re_path

from .consumers import CommentConsumer

srachat_router = URLRouter([
    re_path('^rooms/(?P<id>\w+)/comments/$', CommentConsumer.as_asgi(), name="ws_room_comments"),
])
