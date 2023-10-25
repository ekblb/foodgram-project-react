import io

from django.http import FileResponse
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, get_list_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from foodgram.permissions import AuthorOnly

from .filters import RecipeFilters
from .models import (FavoriteRecipe, Ingredient, Recipe,
                     ShoppingCart, Tag)
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeRetrieveSerializer, RecipeSerializer,
                          TagSerializer, ShoppingCartSerializer,
                          IngredientInRecipe)

import logging


class RecipeViewSet(viewsets.ModelViewSet):
    '''Class for viewing recipes.'''
    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilters

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
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
            if request.user.id == recipe.author.id:
                return Response(
                    {'errors': 'Невозможно добавить свой рецепт в избранное.'},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = RecipeSerializer(recipe,
                                          data=request.data,
                                          context={'request': request},
                                          )
            if serializer.is_valid():
                if not FavoriteRecipe.objects.filter(recipe=recipe,
                                                     user=request.user
                                                     ).exists():
                    FavoriteRecipe.objects.create(recipe=recipe,
                                                  user=request.user
                                                  )
                    return Response(serializer.data,
                                    status=status.HTTP_201_CREATED
                                    )
                return Response(
                    {'errors': 'Рецепт уже добавлен в список избранных.'},
                    status=status.HTTP_400_BAD_REQUEST
                    )
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST
                            )

        if request.method == 'DELETE':
            recipe_delete = FavoriteRecipe.objects.filter(recipe=recipe,
                                                          user=request.user
                                                          )
            if recipe_delete.exists():
                recipe_delete.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Такого рецепта нет в списке избранных.'},
                status=status.HTTP_400_BAD_REQUEST
                )

    @action(methods=['GET'], detail=False)
    def download_shopping_cart(self, request):
        log_str = ''
        
        shopping_cart = ShoppingCart.objects.filter(user=request.user)
        log_str = f'Shopping cart: {shopping_cart}'
        recipes = Recipe.objects.filter(id__in=shopping_cart.values('recipe'))
        log_str += f'\nRecipes: {recipes}'
        ingredients = IngredientInRecipe.objects.select_related('ingredient').filter(
            id__in=recipes.values('ingredients')
            )
        log_str += f'\nIngredients: {ingredients.values()}'
        log_str += f'\nIngredients query: {ingredients.query}'
        
        ingredient_list = log_str + '\nCписок покупок:'
        for obj in ingredients:
            ingredient_list += f'{obj.amount} {obj.ingredient.name}\n'

        # ingredient = Ingredient.objects.filter(
        #     id__in=ingredients.values('ingredient')
        #     ).annotate(sum_amount=Sum('ingredient_in_recipe__amount'))
        # log_str += f'\nIngredient descr: {ingredient.values()}'
        
        # ingredient_name_measurement_unit = ingredient.values(
        #     'name', 'measurement_unit')
        # # .annotate(
        # #     sum_amount=Sum('ingredient_in_recipe__amount'))
        # log_str += f'\ningredient_name_measurement_unit: {ingredient_name_measurement_unit}'
        # ingredient_list = log_str + '\nCписок покупок:'
        # for num, i in enumerate(ingredient_name_measurement_unit):
        #     ingredient_list += (
        #         f"\n{i['name']} - "
        #         # f"{i['sum_amount']} - "
        #         f"{i['measurement_unit']}"
        #     )
        response = HttpResponse(
            ingredient_list, 'Content-Type: application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="shopping_cart.pdf"'
        return response

    @action(methods=['POST', 'DELETE'], detail=True)
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            # if request.user.id == recipe.author.id:
            #     return Response(
            #         {'errors': 'Нельзя добавить свой рецепт в список.'},
            #         status=status.HTTP_400_BAD_REQUEST)
            serializer = RecipeSerializer(recipe,
                                          data=request.data,
                                          context={'request': request},
                                          )
            if serializer.is_valid():
                if not ShoppingCart.objects.filter(recipe=recipe,
                                                   user=request.user
                                                   ).exists():
                    ShoppingCart.objects.create(recipe=recipe,
                                                user=request.user)
                    return Response(serializer.data,
                                    status=status.HTTP_201_CREATED)
                return Response(
                    {'errors': 'Рецепт уже добавлен в список покупок.'},
                    status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST
                            )

        if request.method == 'DELETE':
            recipe_delete = ShoppingCart.objects.filter(recipe=recipe,
                                                        user=request.user)
            if recipe_delete.exists():
                recipe_delete.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Такого рецепта нет в списке покупок.'},
                            status=status.HTTP_400_BAD_REQUEST
                            )


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
