from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.serializers import CustomUserRetrieveSerializer
from drf_extra_fields.fields import Base64ImageField
from django.db import transaction

from .models import (FavoriteRecipe, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)
from .constants import (MIN_AMOUNT, MAX_AMOUNT, MIN_COOKING_TIME,
                        MIN_COOKING_TIME)


class TagSerializer(serializers.ModelSerializer):
    '''
    Serializer for Tag Model (GET method).
    '''
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    '''
    Serializer for Ingredient Model (GET method).
    '''
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeRetrieveSerializer(serializers.ModelSerializer):
    '''
    Serializer for IngredientInRecipe Model (GET method).
    '''
    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientInRecipeCreateSerializer(serializers.ModelSerializer):
    '''
    Serializer for creating instance of IngredientInRecipe Model
    (POST method).
    '''
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(),
                                            write_only=True)
    amount = serializers.IntegerField(min_value=MIN_AMOUNT,
                                      max_value=MAX_AMOUNT,
                                      write_only=True)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeRetrieveSerializer(serializers.ModelSerializer):
    '''
    Serializer for Recipe Model (GET method).
    '''
    author = CustomUserRetrieveSerializer(read_only=True)
    ingredients = IngredientInRecipeRetrieveSerializer(many=True,
                                                       read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time',
                  'is_in_shopping_cart', 'is_favorited')

    def get_is_favorited(self, obj):
        '''
        Method for defining favorite recipes.
        '''
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            user=request.user, author=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        '''
        Method for defining recipes in shopping cart.
        '''
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, author=obj).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    '''
    Serializer for creating or updating instance of Recipe Model
    (POST, PATCH methods).
    '''
    ingredients = IngredientInRecipeCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(min_value=MIN_COOKING_TIME,
                                            max_value=MIN_COOKING_TIME,
                                            write_only=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'name',
                  'image', 'text', 'cooking_time')

    @staticmethod
    def ingredients_index(self, ingredients_data):
        '''
        Method for getting ingredients indexes from getting recipes.
        '''
        ingredients_index = []
        for ingredient in ingredients_data:
            ingredient_object = Ingredient.objects.get(
                id=ingredient['ingredient'])
            ingredient_in_recipe = IngredientInRecipe.objects.bulk_create(
                recipe=id,
                ingredient=ingredient_object,
                amount=ingredient['amount'])
            ingredients_index.append(ingredient_in_recipe.id)
        return ingredients_index

    @transaction.atomic
    def create(self, validated_data):
        '''
        Method for creating new recipe.
        '''
        author = self.context.get('request').user
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        ingredients_index = self.ingredients_index(ingredients_data)
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.ingredients.set(ingredients_index)
        recipe.tags.set(tags_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        '''
        Method for updating recipe.
        '''
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        ingredients_index = self.ingredients_index(ingredients_data)
        IngredientInRecipe.objects.filter(
            id__in=instance.ingredients.all()).delete()
        instance.tags.clear()
        instance.ingredients.clear()
        instance.tags.set(tags_data)
        instance.ingredients.set(ingredients_index)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        '''
        Method for getting response after creating or updating recipe.
        '''
        return RecipeRetrieveSerializer(instance, context=self.context).data


class RecipeSerializer(serializers.ModelSerializer):
    '''
    Serializer for Recipe Model (GET methods).
    '''

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('name', 'cooking_time')


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    '''
    Serializer for creating instance in FavoriteRecipe Model (POST methods).
    '''

    class Meta:
        model = FavoriteRecipe
        fields = ('recipe', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=FavoriteRecipe.objects.all(),
                fields=['recipe', 'user'],
                message='Данный рецепт уже находится в списке Избранных.'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSerializer(
            instance.recipe, context={'request': request}).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    '''
    Serializer for creating instance in ShoppingCart Model (POST methods).
    '''

    class Meta:
        model = ShoppingCart
        fields = ('recipe', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=['recipe', 'user'],
                message='Данный рецепт уже находится в Списке покупок.'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSerializer(
            instance.recipe, context={'request': request}).data
