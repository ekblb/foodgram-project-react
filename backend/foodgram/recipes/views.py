import io

from django.db.models import Sum
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from foodgram.permissions import AuthorOrReadOnly
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import permissions, viewsets
from rest_framework.decorators import action

from .filters import IngredientFilter, RecipeFilters
from .models import FavoriteRecipe, Ingredient, Recipe, ShoppingCart, Tag
from .serializers import (IngredientInRecipe, IngredientSerializer,
                          RecipeCreateSerializer, RecipeRetrieveSerializer,
                          TagSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    '''Class for viewing recipes.'''
    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilters

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return RecipeCreateSerializer
        return RecipeRetrieveSerializer

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return (AuthorOrReadOnly(),)
        return super().get_permissions()

    @action(methods=['POST', 'DELETE'], detail=True)
    def favorite(self, request, pk):
        '''Method for creating and deleting favorite recipe.'''
        if request.method == 'POST':
            return self.add_recipe(FavoriteRecipe, request, pk)
        else:
            return self.delete_recipe(FavoriteRecipe, request, pk)

    def pdf_gen(self, ingredients_annotate):
        '''Method for genereting pdf file which contant list of ingredients.'''
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
        '''Method for downloading user's shopping cart in pdf format.'''
        ingredients_annotate = IngredientInRecipe.objects.filter(
            recipe__shopping_cart_recipe__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(sum_amount=Sum('amount'))

        pdf_ingredients_list = self.pdf_gen(ingredients_annotate)

        response = FileResponse(pdf_ingredients_list,
                                as_attachment=True,
                                filename='shopping_cart.pdf')
        return response

    @action(methods=['POST', 'DELETE'], detail=True)
    def shopping_cart(self, request, pk):
        '''Method for adding and deleting recipes to user's shopping cart.'''
        if request.method == 'POST':
            return self.add_recipe(ShoppingCart, request, pk)
        else:
            return self.delete_recipe(ShoppingCart, request, pk)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''Class for viewing tags.'''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''Class for viewing ingredients.'''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
