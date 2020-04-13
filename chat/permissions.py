from rest_framework import permissions

from chat.models import ChatUser


class IsCreatorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow creators of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the creator of the object.
        return obj.creator == ChatUser.objects.get(user=request.user)


class IsRoomParticipantOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only room participants to leave comments
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        return ChatUser.objects.get(user=request.user) in obj.chat_users.all()
