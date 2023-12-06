from django.shortcuts import get_object_or_404
from recipes.models import Recipe
from rest_framework import serializers

from .models import CustomUser, Subscription


class CustomUserRetrieveSerializer(serializers.ModelSerializer):
    '''
    Serializer for CustomUser Model (GET method).
    '''
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
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')
        read_only_fields = ('email', 'username', 'first_name', 'last_name',
                            'is_subscribed')


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    '''
    Serializer for Recipe Model in SubscriptionRetrieveSerializer serializer
    (GET method).
    '''
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionRetrieveSerializer(CustomUserRetrieveSerializer):
    '''
    Serializer for getting users subscriptions
    (GET method).
    '''
    recipes_count = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)

    def get_recipes_count(self, obj):
        '''
        Method for counting author's recipes.
        '''
        return obj.recipe_author.count()

    def get_recipes(self, obj):
        '''
        Method for getting author's recipes with parameter 'recipes_limit'.
        '''
        recipes = obj.recipe_author.all()
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return SubscriptionRecipeSerializer(recipes, many=True,
                                            context={'request': request}).data

    class Meta(CustomUserRetrieveSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')


class SubscriptionCreateDeleteSerializer(serializers.ModelSerializer):
    '''
    Serializer for creating and deleting subscriptions.
    (POST method).
    '''
    def validate(self, data):
        author = data.get('author')
        user = data.get('user')
        if user == author:
            raise serializers.ValidationError(
                {'errors': 'Подписка на самого себя невозможна.'})
        if Subscription.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                {'errors': 'Подписка уже существует.'})
        return data

    def create(self, validated_data):
        user = self.context.get('request').user
        author = get_object_or_404(CustomUser, pk=validated_data['id'])
        Subscription.objects.create(user=user, author=author)
        serializer = SubscriptionCreateDeleteSerializer(
            author, context={'request': self.context.get('request')})
        return serializer.data

    class Meta:
        model = Subscription
        fields = ('author', 'user')
