from django_filters.rest_framework import FilterSet, filters

from .models import Recipe


class RecipeFilters(FilterSet):
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
        )

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            queryset.filter(favorite__user=user)
            return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            queryset.filter(shopping_cart__user=user)
            return queryset
