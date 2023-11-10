from recipes.models import Recipe
from rest_framework import serializers

from .models import CustomUser, Subscription


class CustomUserRetrieveSerializer(serializers.ModelSerializer):
    '''
    Serializer for CustomUser Model (GET method).
    '''
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        '''
        Method for defining user's subscriptions.
        '''
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj).exists()

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')
        read_only_fields = ('email', 'username', 'first_name', 'last_name',
                            'is_subscribed')


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    '''
    Serializer for Recipe Model in SubscriptionRetrieve serializer
    (GET method).
    '''
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


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


class SubscriptionRetrieveSerializer(CustomUserRetrieveSerializer):
    '''
    Serializer for viewing user's subscriptions
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
        recipes = obj.recipe_author.all()
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
            return SubscriptionRecipeSerializer(
                recipes, many=True, read_only=True).data

    class Meta(CustomUserRetrieveSerializer.Meta):
        model = CustomUser
        fields = ('recipes', 'recipes_count')
