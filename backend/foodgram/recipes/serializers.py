import base64
import imghdr
import uuid

import six
from django.core.files.base import ContentFile
from rest_framework import serializers
from users.serializers import CustomUserRetrieveSerializer

from .models import (FavoriteRecipe, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)


class Base64ImageField(serializers.ImageField):
    '''Class for formating image field to base64.'''
    def to_internal_value(self, data):

        if isinstance(data, six.string_types):
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')

            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            file_name = str(uuid.uuid4())[:12]
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension, )

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


class TagSerializer(serializers.ModelSerializer):
    '''Serializer for Tag Model (GET method).'''
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    '''Serializer for Ingredient Model (GET method).'''
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeRetrieveSerializer(serializers.ModelSerializer):
    '''Serializer for IngredientInRecipe Model (GET method).'''
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientInRecipeCreateSerializer(serializers.ModelSerializer):
    '''Serializer for creating instance of IngredientInRecipe Model
    (POST method).'''
    id = serializers.IntegerField(source='ingredient',
                                  write_only=True,
                                  )
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeRetrieveSerializer(serializers.ModelSerializer):
    '''Serializer for Recipe Model (GET method).'''
    author = CustomUserRetrieveSerializer()
    ingredients = IngredientInRecipeRetrieveSerializer(many=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time',
                  'is_in_shopping_cart', 'is_favorited')

    def get_is_favorited(self, obj):
        '''Method for defining favorite recipes.'''
        if self.context.get('request').user.is_authenticated:
            if FavoriteRecipe.objects.filter(
                recipe=obj.id, user=self.context.get('request').user.id
            ).exists():
                return True
            return False
        return False

    def get_is_in_shopping_cart(self, obj):
        '''Method for defining recipes in shopping cart.'''
        if self.context.get('request').user.is_authenticated:
            if ShoppingCart.objects.filter(
                recipe=obj.id, user=self.context.get('request').user.id
            ).exists():
                return True
            return False
        return False


class RecipeCreateSerializer(serializers.ModelSerializer):
    '''Serializer for creating or updating instance of Recipe Model
    (POST, PATCH methods).'''
    ingredients = IngredientInRecipeCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'name',
                  'image', 'text', 'cooking_time')

    def ingredients_index(self, validated_data):
        '''Method for getting ingredients indexes from getting recipes.'''
        ingredients_data = validated_data.pop('ingredients')
        ingredients_index = []
        for ingredient in ingredients_data:
            ingredient_object = Ingredient.objects.get(
                id=ingredient['ingredient'])
            ingredient_in_recipe = IngredientInRecipe.objects.create(
                ingredient=ingredient_object,
                amount=ingredient['amount'])
            ingredients_index.append(ingredient_in_recipe.id)
        return ingredients_index

    def create(self, validated_data):
        '''Method for creating new recipe.'''
        author = self.context.get('request').user
        tags_data = validated_data.pop('tags')
        ingredients_index = self.ingredients_index(validated_data)
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.ingredients.set(ingredients_index)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        '''Method for updating recipe.'''
        tags_data = validated_data.pop('tags')
        ingredients_index = self.ingredients_index(validated_data)
        super().update(instance, validated_data)
        IngredientInRecipe.objects.filter(
            id__in=instance.ingredients.all()).delete()
        instance.tags.clear()
        instance.ingredients.clear()
        instance.tags.set(tags_data)
        instance.ingredients.set(ingredients_index)
        return instance

    def to_representation(self, instance):
        '''Method for getting response after creating or updating recipe.'''
        serializer = RecipeRetrieveSerializer(instance, context=self.context)
        return serializer.data


class RecipeSerializer(serializers.ModelSerializer):
    '''Serializer for Recipe Model (GET methods).'''
    image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('name', 'cooking_time')
