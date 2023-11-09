from django_filters.rest_framework import (FilterSet,
                                           ModelMultipleChoiceFilter, filters)
from rest_framework.filters import SearchFilter

from .models import Ingredient, Recipe, Tag


class IngredientFilter(SearchFilter):
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilters(FilterSet):
    '''Class for filtering favorite recipes and recipes in shopping cart.'''
    tags = ModelMultipleChoiceFilter(queryset=Tag.objects.all(),
                                     field_name='tags__slug',
                                     to_field_name='slug')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'tags', 'author')

    def filter_is_favorited(self, queryset, name, value):
        request = self.context.get('request')
        if value and request.user.is_authenticated:
            return queryset.filter(favorite_user__user=request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        request = self.context.get('request')
        if value and request.user.is_authenticated:
            return queryset.filter(shopping_cart_user__user=request.user)
        return queryset
