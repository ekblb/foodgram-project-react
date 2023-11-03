from django.contrib.auth.hashers import make_password
from recipes.models import Recipe
from rest_framework import serializers

from .models import CustomUser, Subscription


class CustomUserCreateSerializer(serializers.ModelSerializer):
    '''Serializer for creating instance of CustomUser Model
    (POST method).'''
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name', 'password',
        ]

    def create(self, validated_data):
        '''Method for creating new user.'''
        hash_password = make_password(validated_data.pop('password'))
        new_custom_user = CustomUser.objects.create(password=hash_password,
                                                    **validated_data
                                                    )
        return new_custom_user


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    '''Serializer for Recipe Model in CustomUserSubscribe serializer
    (GET method).'''
    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'image', 'cooking_time',
        ]
        read_only_fields = [
            'id', 'name', 'image', 'cooking_time',
        ]


class CustomUserSubscribeCreateSerializer(serializers.ModelSerializer):
    '''Serializer for creating instance of Subscription Model
    (POST method).'''
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = SubscriptionRecipeSerializer(read_only=True)

    def get_is_subscribed(self, obj):
        '''Method for defining user's subscriptions.'''
        if self.context.get('request').user.is_authenticated:
            if Subscription.objects.filter(
                author=obj.id, user=self.context.get('request').user.id
            ).exists():
                return True
        return False

    def get_recipes_count(self, obj):
        '''Method for counting author's recipes.'''
        recipes_count = Recipe.objects.filter(author=obj.id).count()
        return recipes_count

    class Meta:
        model = CustomUser
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        ]
        read_only_fields = [
            'email', 'username', 'first_name', 'last_name',
        ]


class CustomUserRetrieveSerializer(serializers.ModelSerializer):
    '''Serializer for CustomUser Model (GET method).'''
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        '''Method for defining user's subscriptions.'''
        if self.context.get('request'):
            if Subscription.objects.filter(
                author=obj.id, user=self.context.get('request').user.id
            ).exists():
                return True
        return False

    class Meta:
        model = CustomUser
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed',
        ]
        read_only_fields = [
            'email', 'username', 'first_name', 'last_name', 'is_subscribed'
        ]


class SubscriptionRetrieveSerializer(serializers.ModelSerializer):
    '''Serializer for Subscription Model (GET method).'''
    email = serializers.EmailField(source='author.email')
    id = serializers.IntegerField(source='author.id')
    username = serializers.EmailField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = SubscriptionRecipeSerializer(source='author.recipe_author',
                                           many=True,
                                           read_only=True)
    recipes_count = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        '''Method for defining user's subscriptions.'''
        if self.context.get('request'):
            if Subscription.objects.filter(
                author=obj.id, user=self.context.get('request').user.id
            ).exists():
                return True
        return False

    def get_recipes_count(self, obj):
        '''Method for counting author's recipes.'''
        recipes_count = Recipe.objects.filter(author=obj.author).count()
        return recipes_count

    class Meta:
        model = Subscription
        fields = ['email', 'id', 'username', 'first_name',
                  'last_name', 'recipes', 'recipes_count',
                  'is_subscribed',
                  ]
