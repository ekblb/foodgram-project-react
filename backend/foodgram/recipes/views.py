# import io

# from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from foodgram.permissions import AuthorOnly

from .filters import RecipeFilters
from .models import (FavoriteRecipe, Ingredient, Recipe,
                     ShoppingCart, Tag)
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeRetrieveSerializer, RecipeSerializer,
                          TagSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    '''Class for viewing recipes.'''
    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilters

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return RecipeCreateSerializer
        return RecipeRetrieveSerializer

    def get_permissions(self):
        if self.action in ['update', 'delete']:
            return (AuthorOnly(),)
        return super().get_permissions()

    @action(methods=['POST', 'DELETE'], detail=True)
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            if request.user.id == recipe.author.id:
                return Response(
                    {'errors': 'Невозможно добавить свой рецепт в избранное.'},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = RecipeSerializer(recipe,
                                          data=request.data,
                                          context={'request': request},
                                          )
            if serializer.is_valid():
                if not FavoriteRecipe.objects.filter(recipe=recipe,
                                                     user=request.user
                                                     ).exists():
                    FavoriteRecipe.objects.create(recipe=recipe,
                                                  user=request.user
                                                  )
                    return Response(serializer.data,
                                    status=status.HTTP_201_CREATED
                                    )
                return Response(
                    {'errors': 'Рецепт уже добавлен в список избранных.'},
                    status=status.HTTP_400_BAD_REQUEST
                    )
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST
                            )

        if request.method == 'DELETE':
            recipe_delete = FavoriteRecipe.objects.filter(recipe=recipe,
                                                          user=request.user
                                                          )
            if recipe_delete.exists():
                recipe_delete.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Такого рецепта нет в списке избранных.'},
                status=status.HTTP_400_BAD_REQUEST
                )

    # @action(methods=['GET'], detail=False)
    # def download_shopping_cart(self, request):
    #     # user = request.user
    #     # shopping_cart = ShoppingCart.objects.filter(user=user)
    #     # serializer = ShoppingCartSerializer(shopping_cart, many=True)

    #     return FileResponse(buf, as_attachment=True,
    #                         filename='shopping_cart.pdf')

    @action(methods=['POST', 'DELETE'], detail=True)
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            # if request.user.id == recipe.author.id:
            #     return Response(
            #         {'errors': 'Нельзя добавить свой рецепт в список.'},
            #         status=status.HTTP_400_BAD_REQUEST)
            serializer = RecipeSerializer(recipe,
                                          data=request.data,
                                          context={'request': request},
                                          )
            if serializer.is_valid():
                if not ShoppingCart.objects.filter(recipe=recipe,
                                                   user=request.user
                                                   ).exists():
                    ShoppingCart.objects.create(recipe=recipe,
                                                user=request.user)
                    return Response(serializer.data,
                                    status=status.HTTP_201_CREATED)
                return Response(
                    {'errors': 'Рецепт уже добавлен в список покупок.'},
                    status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST
                            )

        if request.method == 'DELETE':
            recipe_delete = ShoppingCart.objects.filter(recipe=recipe,
                                                        user=request.user)
            if recipe_delete.exists():
                recipe_delete.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Такого рецепта нет в списке покупок.'},
                            status=status.HTTP_400_BAD_REQUEST
                            )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''Class for viewing tags.'''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''Class for viewing ingredients.'''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
