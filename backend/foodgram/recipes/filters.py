from django_filters.rest_framework import (FilterSet, filters,
                                           ModelMultipleChoiceFilter)
from rest_framework.filters import SearchFilter

from .models import Recipe, FavoriteRecipe, ShoppingCart, Tag, Ingredient


class IngredientFilter(SearchFilter):
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilters(FilterSet):
    '''Class for filtering favorite recipes and recipes in shopping cart.'''
    tags = ModelMultipleChoiceFilter(queryset=Tag.objects.all(),
                                     field_name='tags__slug',
                                     to_field_name='slug',
                                     )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
        )

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'tags']

    def filter_is_favorited(self, queryset, name, value):
        # if self.request.user.is_authenticated:
        if value:
            favorite_recipes = FavoriteRecipe.objects.filter(
                user=self.request.user)
            favorite_recipes_id = favorite_recipes.values('recipe')
            filter_queryset = queryset.filter(id__in=favorite_recipes_id)
            return filter_queryset
        return filter_queryset.none()

    def filter_is_in_shopping_cart(self, queryset, name, value):
        # if self.request.user.is_authenticated:
        if value:
            shopping_cart_recipes = ShoppingCart.objects.filter(
                user=self.request.user)
            shopping_cart_recipes_id = shopping_cart_recipes.values('recipe')
            filter_queryset = queryset.filter(id__in=shopping_cart_recipes_id)
            return filter_queryset
        return filter_queryset.none()
