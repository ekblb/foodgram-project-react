from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from .models import (Recipe, Tag, Ingredient, FavoriteRecipe)
from .serializers import (RecipeSerializer, RecipeRetrieveSerializer,
                          RecipeCreateSerializer,
                          TagSerializer, IngredientSerializer,
                          )
from .permissions import AuthorOnly
from .filters import RecipeFilters


class RecipeViewSet(viewsets.ModelViewSet):
    '''Class for viewing recipes.'''
    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilters

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return RecipeCreateSerializer
        return RecipeRetrieveSerializer

    def get_permissions(self):
        if self.action in ['update', 'delete']:
            return (AuthorOnly(),)
        return super().get_permissions()

    @action(methods=['POST', 'DELETE'], detail=True)
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            serializer = RecipeSerializer(recipe,
                                          data=request.data,
                                          context={'request': request},
                                          )
            if serializer.is_valid():
                if not FavoriteRecipe.objects.filter(recipe=recipe,
                                                     user=request.user
                                                     ).exists():
                    FavoriteRecipe.objects.create(recipe=recipe,
                                                  user=request.user)
                    return Response(serializer.data,
                                    status=status.HTTP_201_CREATED)
                return Response({'errors': 'Рецепт уже добавлен в избранное'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''Class for viewing tags.'''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''Class for viewing ingredients.'''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
