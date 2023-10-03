from rest_framework.mixins import (ListModelMixin,
                                   CreateModelMixin,
                                   DestroyModelMixin)
from rest_framework.viewsets import GenericViewSet


class ListCreateDestroyMixinSet(ListModelMixin,
                                CreateModelMixin,
                                DestroyModelMixin,
                                GenericViewSet
                                ):
    pass
