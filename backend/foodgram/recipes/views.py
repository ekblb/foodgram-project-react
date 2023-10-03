from rest_framework import viewsets
# from rest_framework.decorators import action
# from rest_framework.response import Response
from .models import (Recipe, Tag, Ingredient, FavoriteRecipe, ShoppingCart,)
from .serializers import (RecipeGetSerializer, RecipePostSerializer,
                          TagSerializer,
                          IngredientSerializer, FavoriteRecipeSerializer,
                          ShoppingCartSerializer,)
from .mixins import CreateDestroyMixinSet


class RecipeViewSet(viewsets.ModelViewSet):
    '''Class for viewing recipes.'''
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.request == 'POST':
            return RecipePostSerializer
        return RecipeGetSerializer

    # @action(url_path='download_shopping_cart')
    # def download_shopping_cart(self, request):

    # def get_serializer_class(self):
    #     if self.action == 'shopping_cart':
    #         return ShoppingCartSerializer
    #     return RecipeSerializer

    # @action(methods=['post'],
    #         detail=True, url_path='shopping_cart')
    # def shopping_cart(self, request, pk=None):
    #     if request.method == 'POST':
    #         serializer = ShoppingCartSerializer(data=request.data)
    #         if serializer.is_valid():
    #             serializer.save()
    #             ShoppingCart.objects.create(recipe=pk, user=request.user)
    #             return Response(serializer.data,
    #                             status=status.HTTP_201_CREATED)
    #         return Response(serializer.errors,
    #                         status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''Class for viewing tags.'''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''Class for viewing ingredients.'''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class FavoriteRecipeViewSet(CreateDestroyMixinSet):
    '''Class for viewing favorite recipes.'''
    queryset = FavoriteRecipe.objects.all()
    serializer_class = FavoriteRecipeSerializer


# class ShoppingCartViewSet(ListCreateDestroyMixinSet):
class ShoppingCartViewSet(viewsets.ModelViewSet):
    '''Class for viewing favorite recipes.'''
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
