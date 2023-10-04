from rest_framework import viewsets, permissions
from .models import (Recipe, Tag, Ingredient, FavoriteRecipe, ShoppingCart,)
from .serializers import (RecipeGetSerializer, RecipePostSerializer,
                          TagGetSerializer, IngredientSerializer,
                          FavoriteRecipeSerializer, ShoppingCartSerializer,
                          )
from .mixins import CreateDestroyMixinSet
from .permissions import AuthorOnly


class RecipeViewSet(viewsets.ModelViewSet):
    '''Class for viewing recipes.'''
    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return RecipePostSerializer
        return RecipeGetSerializer

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return (AuthorOnly(),)
        return super().get_permissions()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''Class for viewing tags.'''
    queryset = Tag.objects.all()
    serializer_class = TagGetSerializer
    pagination_class = None
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''Class for viewing ingredients.'''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


class FavoriteRecipeViewSet(CreateDestroyMixinSet):
    '''Class for viewing favorite recipes.'''
    queryset = FavoriteRecipe.objects.all()
    serializer_class = FavoriteRecipeSerializer


class ShoppingCartViewSet(viewsets.ModelViewSet):
    '''Class for viewing favorite recipes.'''
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
