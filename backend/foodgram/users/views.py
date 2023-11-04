from django.shortcuts import get_list_or_404, get_object_or_404
from djoser.serializers import SetPasswordSerializer
from rest_framework import pagination, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import CustomUser, Subscription
from .serializers import (CustomUserCreateSerializer,
                          CustomUserRetrieveSerializer,
                          CustomUserSubscribeCreateSerializer,
                          SubscriptionRetrieveSerializer,
                          )


class CustomUserViewSet(viewsets.ModelViewSet):
    '''Class for viewing users.'''
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.AllowAny, )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CustomUserCreateSerializer
        return CustomUserRetrieveSerializer

    @action(methods=['GET'],
            detail=False,
            permission_classes=[permissions.IsAuthenticated]
            )
    def me(self, request):
        '''Method for getting current user.'''
        me = get_object_or_404(CustomUser, id=request.user.id)
        serializer = CustomUserRetrieveSerializer(me)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST'],
            detail=False,
            permission_classes=[permissions.IsAuthenticated]
            )
    def set_password(self, request):
        '''Method for changing password.'''
        serializer = SetPasswordSerializer(data=request.data,
                                           context={'request': request}
                                           )
        if serializer.is_valid():
            if serializer.data["new_password"] == serializer.data["current_password"]:
                return Response({'errors': 'Пароли совпадают.'},
                                status=status.HTTP_400_BAD_REQUEST
                                )
            self.request.user.set_password(serializer.data["new_password"])
            self.request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST
                        )

    @action(methods=['GET'], detail=False,
            permission_classes=[permissions.IsAuthenticated],)
    def subscriptions(self, request):
        '''Method for getting current user's subscriptions.'''
        subscriptions = get_list_or_404(Subscription, user=request.user)
        paginator = pagination.PageNumberPagination()
        page = paginator.paginate_queryset(subscriptions, request)
        pagination_class = (pagination.PageNumberPagination,)
        # subscriptions = Subscription.objects.filter(
        #     user=request.user).select_related('author')

        serializer = SubscriptionRetrieveSerializer(page, subscriptions,
                                                    context={'request': request},
                                                    many=True)
        return Response(paginator.get_paginated_response(serializer.data), status=status.HTTP_200_OK)

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, pk):
        '''Method for creating and deleting user's subscription.'''
        author = get_object_or_404(CustomUser, id=pk)

        if request.method == 'POST':
            if request.user.id == author.id:
                return Response(
                    {'errors': 'Подписка на самого себя невозможна.'},
                    status=status.HTTP_400_BAD_REQUEST
                    )
            serializer = CustomUserSubscribeCreateSerializer(
                author,
                data=request.data, context={'request': request}
                )
            if serializer.is_valid():
                if not Subscription.objects.filter(author=author,
                                                   user=request.user).exists():
                    Subscription.objects.create(author=author,
                                                user=request.user
                                                )
                    return Response(serializer.data,
                                    status=status.HTTP_201_CREATED
                                    )
                return Response(
                    {'errors': 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                    )
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST
                            )

        if request.method == 'DELETE':
            subscription_delete = Subscription.objects.filter(
                author=author,
                user=request.user
            )
            if subscription_delete.exists():
                subscription_delete.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'У вас нет подписки на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
                )
