from django.urls import include, path
from rest_framework.routers import DefaultRouter

from chat.views import comments, rooms

router = DefaultRouter()
router.register(r'comments', comments.CommentViewSet)
router.register(r'rooms', rooms.RoomViewSet)

urlpatterns = [
    path('', include(router.urls)),
]


