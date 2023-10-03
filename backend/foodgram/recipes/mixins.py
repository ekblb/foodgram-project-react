from rest_framework.mixins import (CreateModelMixin,
                                   DestroyModelMixin)
from rest_framework.viewsets import GenericViewSet


class CreateDestroyMixinSet(CreateModelMixin,
                            DestroyModelMixin,
                            GenericViewSet,
                            ):
    pass
