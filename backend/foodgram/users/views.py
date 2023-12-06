from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import pagination, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response


from .models import CustomUser, Subscription
from .serializers import (SubscriptionRetrieveSerializer,
                          SubscriptionCreateDeleteSerializer,
                          CustomUserRetrieveSerializer)


class CustomUserViewSet(UserViewSet):
    '''
    Class for viewing users.
    '''
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = CustomUserRetrieveSerializer

    @action(methods=['GET'], detail=False,
            permission_classes=[permissions.IsAuthenticated],
            pagination_class=pagination.PageNumberPagination)
    def subscriptions(self, request):
        '''
        Method for getting current user's subscriptions.
        '''
        user = self.request.user
        subscriptions = user.subscription_author.all()
        # subscriptions = CustomUser.objects.filter(
        #     subscription_author__user=user)
        subscriptions_page = self.paginate_queryset(subscriptions)
        serializer = SubscriptionRetrieveSerializer(
            subscriptions_page, context={'request': request}, many=True)
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, pk):
        '''
        Method for creating and deleting user's subscription.
        '''
        author = get_object_or_404(CustomUser, id=pk)

        if request.method == 'POST':
            serializer = SubscriptionCreateDeleteSerializer(
                author, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(author=author, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription_delete = Subscription.objects.filter(
                author=author, user=request.user)
            if subscription_delete.delete():
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'У вас нет подписки на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST)
