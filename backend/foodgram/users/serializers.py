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
    Serializer for Recipe Model in CustomUserSubscribe serializer
    (GET method).
    '''
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionRetrieveSerializer(CustomUserRetrieveSerializer):
    '''
    Serializer for getting instance of Subscription Model
    (GET method).
    '''
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    def get_recipes_count(self, obj):
        '''
        Method for counting author's recipes.
        '''
        return Recipe.objects.filter(author=obj.id).count()

    def get_recipes(self, obj):
        '''
        Method for getting author's recipes with parameter 'recipes_limit'.
        '''
        recipes = obj.subscription_author.recipe_author.all()
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
        return data

    class Meta:
        model = Subscription
        fields = ('author', 'user')
