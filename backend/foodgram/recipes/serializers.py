from rest_framework import serializers

from .models import Ingredient, Recipe, Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit', ]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug', ]


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        ingredients = IngredientSerializer()

        model = Recipe
        fields = [
           'id' 'name', 'image', 'text', 'ingredients',
           'tags', 'cooking_time',
        ]
