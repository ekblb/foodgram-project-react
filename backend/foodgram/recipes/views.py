import io

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from foodgram.permissions import AuthorOnly
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import RecipeFilters, IngredientFilter
from .models import FavoriteRecipe, Ingredient, Recipe, ShoppingCart, Tag
from .serializers import (IngredientInRecipe, IngredientSerializer,
                          RecipeCreateSerializer, RecipeRetrieveSerializer,
                          RecipeSerializer, TagSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    '''Class for viewing recipes.'''
    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilters

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return RecipeCreateSerializer
        return RecipeRetrieveSerializer

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return (AuthorOnly(),)
        return super().get_permissions()

    @action(methods=['POST', 'DELETE'], detail=True)
    def favorite(self, request, pk):
        '''Method for creating and deleting favorite recipe.'''
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            # if request.user.id == recipe.author.id:
            #     return Response(
            #         {'errors': 'Невозможно добавить свой рецепт в избранное.'},
            #         status=status.HTTP_400_BAD_REQUEST)
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

    def pdf_gen(self, ingredients_annotate):
        '''Method for genereting pdf file which contant list of ingredients.'''
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
        pdfmetrics.registerFont(TTFont('FreeSans', 'recipes/FreeSans.ttf'))
        textobj = c.beginText()
        textobj.setTextOrigin(inch, inch)
        textobj.setFont('FreeSans', 14)

        ingredients_list = ['Cписок покупок:']

        for i in ingredients_annotate:
            ingredients_list.append(f"- {i['ingredient__name']} "
                                    f"({i['ingredient__measurement_unit']}) - "
                                    f"{i['sum_amount']}")
        for obj in ingredients_list:
            textobj.textLine(obj)

        c.drawText(textobj)
        c.showPage()
        c.save()
        buf.seek(0)

        return buf

    @action(methods=['GET'], detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        '''Method for downloading user's shopping cart in pdf format.'''
        shopping_cart = ShoppingCart.objects.filter(user=request.user)
        recipes = Recipe.objects.filter(id__in=shopping_cart.values('recipe'))
        ingredients = IngredientInRecipe.objects.select_related(
            'ingredient').filter(id__in=recipes.values('ingredients'))
        ingredients_annotate = ingredients.values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
            sum_amount=Sum('amount'))

        pdf_ingredients_list = self.pdf_gen(ingredients_annotate)

        response = FileResponse(pdf_ingredients_list,
                                as_attachment=True,
                                filename='shopping_cart.pdf',)
        return response

    @action(methods=['POST', 'DELETE'], detail=True)
    def shopping_cart(self, request, pk):
        '''Method for adding and deleting recipes to user's shopping cart.'''
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
    filterset_class = IngredientFilter
