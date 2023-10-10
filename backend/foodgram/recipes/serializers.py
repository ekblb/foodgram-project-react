from rest_framework import serializers

from .models import (Ingredient, Recipe, Tag, IngredientInRecipe,
                     FavoriteRecipe, ShoppingCart,
                     )
from users.serializers import CustomUserRetrieveSerializer


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid

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
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug', ]


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit', ]


class IngredientInRecipeRetrieveSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        )

    class Meta:
        model = IngredientInRecipe
        fields = ['id', 'name', 'measurement_unit', 'amount', ]


class IngredientInRecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient')

    class Meta:
        model = IngredientInRecipe
        fields = ['id', 'amount', ]


class RecipeRetrieveSerializer(serializers.ModelSerializer):

    author = CustomUserRetrieveSerializer()
    ingredients = IngredientInRecipeRetrieveSerializer(many=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
           'id', 'tags', 'author', 'ingredients', 'is_favorited',
           'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        ]

    def get_is_favorited(self, obj):
        if self.context.get('request').user.is_authenticated:
            if FavoriteRecipe.objects.filter(
                recipe=obj.id, user=self.context.get('request').user.id
            ).exists():
                return True
            return False
        return False

    def get_is_in_shopping_cart(self, obj):
        if ShoppingCart.objects.filter(
            recipe=obj.id, user=self.context.get('request').user.id
        ).exists():
            return True
        return False


class RecipeCreateSerializer(serializers.ModelSerializer):

    ingredients = IngredientInRecipeCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(many=True, read_only='True')
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
           'ingredients', 'tags', 'name', 'image', 'text',
           'cooking_time',
        ]

    def create(self, validated_data):
        author = self.context.get('request').user.id
        validated_data.update({'author_id': author})
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)

        for ingredient in ingredients:
            IngredientInRecipe.objects.create(
                amount=ingredient['amount'],
                ingredient=ingredient['ingredient'],
                )
        return recipe

    # def update(self, validated_data):


class RecipeSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()
    image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = [
           'id', 'name', 'image', 'cooking_time',
        ]


class ShoppingCartRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = [
           'id', 'name', 'image', 'cooking_time',
        ]


class SubscriptionRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = [
           'id', 'name', 'image', 'cooking_time',
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    # id = ShoppingCartRecipeSerializer(source='recipe.id')

    class Meta:
        model = ShoppingCart
        fields = ['id']
