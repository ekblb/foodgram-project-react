from rest_framework import serializers
from .models import CustomUser, Subscription
from recipes.models import Recipe


class CustomUserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name',
        ]
        read_only_fields = [
            'email', 'username', 'first_name', 'last_name',
        ]


class SubscriptionRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'image', 'cooking_time',
        ]
        read_only_fields = [
            'id', 'name', 'image', 'cooking_time',
        ]


class CustomUserSubscribeCreateSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = SubscriptionRecipeSerializer(read_only=True)

    def get_is_subscribed(self, obj):
        if self.context.get('request').user.is_authenticated:
            if Subscription.objects.filter(
                author=obj.id, user=self.context.get('request').user.id
            ).exists():
                return True
        return False

    def get_recipes_count(self, obj):
        recipes_count = Recipe.objects.filter(author=obj.id).count()
        return recipes_count

    class Meta:
        model = CustomUser
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed',
            'recipes', 'recipes_count',
        ]
        read_only_fields = [
            'email', 'username', 'first_name', 'last_name',
        ]


class CustomUserRetrieveSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        if self.context.get('request').user.is_authenticated:
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
    email = serializers.EmailField(source='author.email')
    id = serializers.IntegerField(source='author.id')
    username = serializers.EmailField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    # is_subscribed = serializers.SerializerMethodField()
    recipes = SubscriptionRecipeSerializer(source='author.recipes',
                                           many=True,
                                           read_only=True)
    recipes_count = serializers.SerializerMethodField()

    # def get_is_subscribed(self, obj):
    #     if self.context.get('request').user.is_authenticated:
    #         if Subscription.objects.filter(
    #             author=obj.id, user=self.context.get('request').user.id
    #         ).exists():
    #             return True
    #     return False

    def get_recipes_count(self, obj):
        recipes_count = Recipe.objects.filter(author=obj.author).count()
        return recipes_count

    class Meta:
        model = Subscription
        fields = ['email', 'id', 'username', 'first_name',
                  'last_name', 'recipes', 'recipes_count',
                    #'is_subscribed'
                  ]
