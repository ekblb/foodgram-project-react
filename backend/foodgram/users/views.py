from rest_framework import viewsets, permissions, decorators, response
from .models import CustomUser, Subscription
from .serializers import (CustomUserRetrieveSerializer,
                          CustomUserCreateSerializer,
                          SubscriptionSerializer
                          )
from .mixins import ListCreateDestroyMixinSet


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        return CustomUserRetrieveSerializer


class SubscriptionViewSet(ListCreateDestroyMixinSet):
    '''Class for viewing subscriptions.'''
    serializer_class = SubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        subscriptions = Subscription.objects.filter(
            user=self.request.user.id)
        return subscriptions
