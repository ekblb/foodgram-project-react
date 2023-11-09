import io

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .permissions import IsAuthorOrReadOnly
from .pagination import LimitPageNumberPagination

from .filters import IngredientFilter, RecipeFilters
from .models import FavoriteRecipe, Ingredient, Recipe, ShoppingCart, Tag
from .serializers import (IngredientInRecipe, IngredientSerializer,
                          RecipeCreateSerializer, RecipeRetrieveSerializer,
                          TagSerializer, ShoppingCartSerializer,
                          FavoriteRecipeSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    '''
    Class for viewing recipes.
    '''
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilters

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return RecipeCreateSerializer
        return RecipeRetrieveSerializer

    def pdf_gen(self, ingredients_annotate):
        '''
        Method for genereting pdf file which contant list of ingredients.
        '''
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
        pdfmetrics.registerFont(
            TTFont('FreeSans', 'recipes/fonts/FreeSans.ttf'))
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
        '''
        Method for downloading user's shopping cart in pdf format.
        '''
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_cart_recipe__user=request.user).values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
            sum_amount=Sum('amount')).order_by('ingredient__name')

        pdf_ingredients_list = self.pdf_gen(ingredients)

        response = FileResponse(pdf_ingredients_list, as_attachment=True,
                                filename='shopping_cart.pdf')
        return response

    @staticmethod
    def create_instance(serializer_outer, request, pk):
        '''
        Method for creating instance in FavoriteRecipe or ShoppingCart Models.
        '''
        recipe_user = {'user': request.user.id, 'recipe': pk}
        serializer = serializer_outer(data=recipe_user,
                                      context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Рецепт успешно добавлен.'},
                        status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_instance(model, request, pk):
        '''
        Method for deleting instance in FavoriteRecipe or ShoppingCart Models.
        '''
        get_object_or_404(model, user=request.user,
                          recipe=get_object_or_404(Recipe, pk=pk)).delete()
        return Response({'message': 'Рецепт успешно удален.'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(methods=['POST', 'DELETE'], detail=True)
    def shopping_cart(self, request, pk):
        '''
        Method for adding and deleting recipes to user's shopping cart.
        '''
        if request.method == 'POST':
            return self.create_instance(ShoppingCartSerializer, request, pk)
        elif request.method == 'DELETE':
            return self.delete_instance(ShoppingCart, request, pk)

    @action(methods=['POST', 'DELETE'], detail=True)
    def favorite(self, request, pk):
        '''
        Method for adding and deleting favorite recipes.
        '''
        if request.method == 'POST':
            return self.create_instance(FavoriteRecipeSerializer, request, pk)
        elif request.method == 'DELETE':
            return self.delete_instance(FavoriteRecipe, request, pk)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    Class for viewing tags.
    '''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    Class for viewing ingredients.
    '''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
