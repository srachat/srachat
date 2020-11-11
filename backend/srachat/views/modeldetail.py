from typing import Type

from rest_framework import mixins, serializers

from rest_framework.viewsets import GenericViewSet


class ModelDetail(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  GenericViewSet):
    """
    This view is able to display, update and delete a single room.
    # TODO: extend the documentation. Describe all permissions.
    """
    permission_classes = None
    queryset = None

    update_serializer_class = None
    detail_serializer_class = None

    default_actions = {
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy"
    }

    @classmethod
    def as_view(cls, **kwargs):
        actions = kwargs.get("actions", None)
        if not actions:
            actions = cls.default_actions
        return super().as_view(actions=actions, **kwargs)

    def get_serializer_class(self) -> Type[serializers.ModelSerializer]:
        _cls = self.__class__
        if self.action in ("update", "partial_update"):
            return _cls.update_serializer_class
        else:
            return _cls.detail_serializer_class
