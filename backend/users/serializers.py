from rest_framework import serializers, validators

from recipes.models import Recipe
from users.models import Subscription, User


class UserRetrieveSerializer(serializers.ModelSerializer):
    """
    Serializer for User Model (GET method).
    """
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        '''Method for defining user's subscriptions.'''
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and Subscription.objects.filter(author=obj.id,
                                                user=request.user.id).exists())

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')
        read_only_fields = ('email', 'username', 'first_name', 'last_name',
                            'is_subscribed')


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    """
    Serializer for Recipe Model in SubscriptionRetrieveSerializer serializer
    (GET method).
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionRetrieveSerializer(UserRetrieveSerializer):
    """
    Serializer for getting users subscriptions
    (GET method).
    """
    recipes_count = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)

    def get_recipes_count(self, obj):
        '''
        Method for counting authozr's recipes.
        '''
        return obj.recipe_author.count()

    def get_recipes(self, obj):
        """
        Method for getting author's recipes with parameter 'recipes_limit'.
        """
        recipes = obj.recipe_author.all()
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return SubscriptionRecipeSerializer(recipes, many=True,
                                            context={'request': request}).data

    class Meta(UserRetrieveSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and deleting subscriptions.
    (POST method).
    """
    def validate(self, data):
        user = data.get('user')
        author = data.get('author')
        if user == author:
            raise serializers.ValidationError(
                {'errors': 'Подписка на самого себя невозможна.'})
        return data

    class Meta:
        model = Subscription
        fields = ('author', 'user')
        validators = [validators.UniqueTogetherValidator(
            queryset=Subscription.objects.all(),
            fields=('author', 'user'),
            message='Подписка уже существует.')]
