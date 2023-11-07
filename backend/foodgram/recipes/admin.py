from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import (FavoriteRecipe, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)


class IngredientResource(resources.ModelResource):
    class Meta:
        model = Ingredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'author', 'author_id', 'favorite_recipes']
    list_filter = ['author', 'name', 'tags']

    def favorite_recipes(self, obj: Recipe):
        return obj.favorite_recipe.count()


@admin.register(Ingredient)
class IngredientAdmin(ImportExportModelAdmin):
    resource_class = IngredientResource
    list_display = ['id', 'name', 'measurement_unit']
    list_filter = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'color', 'slug']


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ['id', 'ingredient', 'amount']


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ['id', 'recipe', 'user']
    list_filter = ['recipe', 'user']


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ['id', 'recipe', 'user']
    list_filter = ['recipe', 'user']
