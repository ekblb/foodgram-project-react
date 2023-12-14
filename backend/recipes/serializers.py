from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from users.serializers import CustomUserRetrieveSerializer

from .models import (FavoriteRecipe, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for Tag Model (GET method).
    """
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """
    Serializer for Ingredient Model (GET method).
    """
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeRetrieveSerializer(serializers.ModelSerializer):
    """
    Serializer for IngredientInRecipe Model (GET method).
    """
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """
    Serializer for creating instance of IngredientInRecipe Model
    (POST method).
    """
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeRetrieveSerializer(serializers.ModelSerializer):
    """
    Serializer for Recipe Model (GET method).
    """
    author = CustomUserRetrieveSerializer(read_only=True)
    ingredients = IngredientInRecipeRetrieveSerializer(
        source='recipe_ingredients', many=True)
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time',
                  'is_in_shopping_cart', 'is_favorited')

    def get_is_favorited(self, obj):
        """
        Method for defining favorite recipes.
        """
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and FavoriteRecipe.objects.filter(
                    recipe=obj.id,
                    user=self.context.get('request').user.id).exists())

    def get_is_in_shopping_cart(self, obj):
        """
        Method for defining recipes in shopping cart.
        """
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and ShoppingCart.objects.filter(
                    recipe=obj.id,
                    user=self.context.get('request').user.id).exists())


class RecipeSerializer(serializers.ModelSerializer):
    """
    Serializer for Recipe Model (GET methods).
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('name', 'cooking_time')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating or updating instance of Recipe Model
    (POST, PATCH methods).
    """
    ingredients = IngredientInRecipeSerializer(source='recipe_ingredients',
                                               many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'name',
                  'image', 'text', 'cooking_time')

    def validate(self, data):
        ingredients = data['recipe_ingredients']
        tags = data.get('tags')

        if ingredients:
            ingredients_list = []
            for ingredient in ingredients:
                ingredient_id = ingredient['id']
                if ingredient_id in ingredients_list:
                    raise ValueError(
                        {'errors': 'Данный ингредиент уже добавлен в рецепт.'})
                ingredients_list.append(ingredient_id)
                return data
        raise ValueError({'errors': 'В рецепте отсутствуют ингредиенты.'})

    @transaction.atomic
    def create(self, validated_data):
        """
        Method for creating new recipe.
        """
        author = self.context.get('request').user
        ingredients_data = validated_data.pop('recipe_ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags_data)
        ingredients_index(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Method for updating recipe.
        """
        if 'recipe_ingredients' in validated_data:
            ingredients_data = validated_data.pop('recipe_ingredients')
            instance.ingredients.clear()
            ingredients_index(instance, ingredients_data)
        if 'tags' in validated_data:
            instance.tags.set(validated_data.pop('tags'))
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """
        Method for getting response after creating or updating recipe.
        """
        serializer = RecipeRetrieveSerializer(instance,
                                              context=self.context)
        return serializer.data


def ingredients_index(recipe, ingredients_data):
    """
    Method for getting ingredients indexes from getting recipes.
    """
    ingredients_index = []
    for ingredient in ingredients_data:
        ingredients_index.append(IngredientInRecipe(
            recipe=recipe, ingredient=ingredient['id'],
            amount=ingredient['amount']))
    IngredientInRecipe.objects.bulk_create(ingredients_index)
