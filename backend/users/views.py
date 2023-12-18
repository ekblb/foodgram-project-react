from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from foodgram.pagination import PageNumberLimitPagination

from .models import User, Subscription
from .serializers import (UserRetrieveSerializer,
                          SubscriptionCreateSerializer,
                          SubscriptionRetrieveSerializer)


class UserViewSet(UserViewSet):
    """
    Class for viewing users.
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    pagination_class = PageNumberLimitPagination
    serializer_class = UserRetrieveSerializer

    @action(detail=False, methods=['GET'],
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """
        Method for getting current user's profile.
        """
        user = self.request.user
        serializer = UserRetrieveSerializer(
            user, context={'request': request})
        return Response(serializer.data)

    @action(methods=['GET'], detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        """
        Method for getting current user's subscriptions.
        """
        user = request.user
        subscriptions = User.objects.filter(
            subscription_author__user=user)
        subscriptions_page = self.paginate_queryset(subscriptions)
        serializer = SubscriptionRetrieveSerializer(
            subscriptions_page, context={'request': request}, many=True)
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id):
        """
        Method for creating and deleting user's subscription.
        """
        user = request.user
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            if user == author:
                return Response({
                    'errors': 'Вы не можете подписываться на самого себя'
                }, status=status.HTTP_400_BAD_REQUEST)
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response({
                    'errors': 'Вы уже подписаны на данного пользователя'
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer = SubscriptionCreateSerializer(
                data={'user': user.id, 'author': author.id})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = SubscriptionRetrieveSerializer(
                author, context={'request': request},
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if user == author:
            return Response({
                'errors': 'Вы не можете отписываться от самого себя'},
                status=status.HTTP_400_BAD_REQUEST)

        subscription = Subscription.objects.filter(user=user, author=author)
        if not subscription.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
