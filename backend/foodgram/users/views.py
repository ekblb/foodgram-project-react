from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_list_or_404, get_object_or_404

from .models import CustomUser, Subscription
from .serializers import (CustomUserRetrieveSerializer,
                          CustomUserCreateSerializer,
                          SubscriptionRetrieveSerializer,
                          CustomUserSubscribeCreateSerializer
                          )


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        return CustomUserRetrieveSerializer

    @action(methods=['GET'], detail=False)
    def subscriptions(self, request):
        user = request.user
        subscriptions = get_list_or_404(Subscription, user=user)
        serializer = SubscriptionRetrieveSerializer(subscriptions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST', 'DELETE'], detail=True)
    def subscribe(self, request, pk):
        author = get_object_or_404(CustomUser, id=pk)

        if request.method == 'POST':
            if request.user.id == author.id:
                return Response({'errors': 'Подписка на самого себя невозможна.'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = CustomUserSubscribeCreateSerializer(author,
                                                             data=request.data,
                                                             context={'request': request}
                                                             )
            if serializer.is_valid():
                if not Subscription.objects.filter(author=author,
                                                   user=request.user).exists():
                    Subscription.objects.create(author=author,
                                                user=request.user)
                    return Response(serializer.data,
                                    status=status.HTTP_201_CREATED)
                return Response({'errors': 'Вы уже подписаны на этого пользователя.'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            subscription_delete = Subscription.objects.filter(author=author,
                                                              user=request.user)
            if subscription_delete.exists():
                subscription_delete.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'У вас нет подписки на этого пользователя.'},
                            status=status.HTTP_400_BAD_REQUEST)
