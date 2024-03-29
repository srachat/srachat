from rest_framework import permissions

from .models import Room
from .models.user import ChatUser


class AbstractSrachatReadOnlyPermission(permissions.BasePermission):
    """
    Abstract class for all *OrReadOnlyPermissions.

    It implements the read only part of the permissions.BasePermission has_object_permission method.
    The only part that should be changed in the subclasses is the `condition` class variable.
    """

    @staticmethod
    def get_condition(request, view, obj) -> bool:
        return True

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        return self.__class__.get_condition(request, view, obj)


class IsCreatorOrReadOnly(AbstractSrachatReadOnlyPermission):
    """
    Custom permission to only allow creators of an object to edit it.
    """

    @staticmethod
    def get_condition(request, view, obj) -> bool:
        return obj.creator == ChatUser.objects.get(user=request.user)


class IsRoomParticipantOrReadOnly(AbstractSrachatReadOnlyPermission):
    """
    Custom permission to allow only room participants to leave comments
    """

    @staticmethod
    def get_condition(request, view, obj) -> bool:
        return ChatUser.objects.get(user=request.user) in obj.chat_users.all()


class IsRoomAdminOrReadOnly(AbstractSrachatReadOnlyPermission):
    """
    Custom permission to allow only room admins to change the info about the room
    """

    @staticmethod
    def get_condition(request, view, obj) -> bool:
        return ChatUser.objects.get(user=request.user) in obj.admins.all()


class IsAccountOwnerOrReadOnly(AbstractSrachatReadOnlyPermission):
    """
    Custom permission to only account owner can change some info about themselves
    """

    @staticmethod
    def get_condition(request, view, obj) -> bool:
        return obj.user == request.user


class IsAllowedRoomOrReadOnly(AbstractSrachatReadOnlyPermission):
    """
    Custom permission to check whether user is performing action in an allowed room
    """

    @staticmethod
    def get_condition(request, view, obj) -> bool:
        if isinstance(obj, Room):
            room = obj
        elif hasattr(obj, "room"):
            room = obj.room
        else:
            raise ValueError("Object should either be of type Room or any type, which is bound to room.")

        user = ChatUser.objects.get(user=request.user)
        if user in room.banned_users.all() and user not in room.admins.all() and user is not room.creator:
            return False
        return True
