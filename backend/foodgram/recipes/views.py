from rest_framework import viewsets
from .models import (
    Recipe,
    Tag,
    Ingredient,
    Subscription,
    FavoriteRecipe,
    ShoppingCart,
    )
from .serializers import (
    RecipeSerializer,
    TagSerializer,
    IngredientSerializer,
    SubscriptionSerializer,
    FavoriteRecipeSerializer,
    ShoppingCartSerializer,
    )
from .mixins import ListCreateDestroyMixinSet, CreateDestroyMixinSet


class RecipeViewSet(viewsets.ModelViewSet):
    '''Class for viewing recipes.'''
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


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


class SubscriptionViewSet(ListCreateDestroyMixinSet):
    '''Class for viewing subscriptions.'''
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer


class FavoriteRecipeViewSet(CreateDestroyMixinSet):
    '''Class for viewing favorite recipes.'''
    queryset = FavoriteRecipe.objects.all()
    serializer_class = FavoriteRecipeSerializer


class ShoppingCartViewSet(ListCreateDestroyMixinSet):
    '''Class for viewing favorite recipes.'''
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
