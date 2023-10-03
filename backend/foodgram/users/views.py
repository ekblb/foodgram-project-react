from rest_framework import viewsets
from .models import CustomUser, Subscription
from .serializers import CustomUserSerializer, SubscriptionSerializer
from .mixins import ListCreateDestroyMixinSet


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class SubscriptionViewSet(ListCreateDestroyMixinSet):
    '''Class for viewing subscriptions.'''
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
