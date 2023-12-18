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

from foodgram.pagination import PageNumberLimitPagination
from foodgram.permissions import AuthorOrReadOnly

from recipes.filters import IngredientFilter, RecipeFilters
from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            ShoppingCart, Tag)
from recipes.serializers import (FavoriteRecipeSerializer, IngredientInRecipe,
                                 IngredientSerializer, RecipeCreateSerializer,
                                 RecipeRetrieveSerializer,
                                 ShoppingCartSerializer,
                                 TagSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Class for viewing recipes.
    """
    queryset = Recipe.objects.all()
    pagination_class = PageNumberLimitPagination
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilters

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return RecipeCreateSerializer
        return RecipeRetrieveSerializer

    def add_recipe(self, serializer_name, request, pk):
        """
        Method for adding recipe to Favorite or to Shopping Cart.
        """
        serializer = serializer_name(
            data={'user': request.user.id, 'recipe': pk},
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, model, request, pk):
        """
        Method for deleting recipe from Favorite or from Shopping Cart.
        """
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        recipe_delete = model.objects.filter(recipe=recipe, user=user).delete()
        if recipe_delete[0] == 0:
            return Response('Данный рецепт не добавлен.',
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['POST', 'DELETE'], detail=True)
    def favorite(self, request, pk):
        """
        Method for creating and deleting favorite recipe.
        """
        if request.method == 'POST':
            return self.add_recipe(FavoriteRecipeSerializer, request, pk)
        return self.delete_recipe(FavoriteRecipe, request, pk)

    def pdf_gen(self, ingredients_annotate):
        """
        Method for genereting pdf file which contant list of ingredients.
        """
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
        """
        Method for downloading user's shopping cart in pdf format.
        """
        ingredients_annotate = IngredientInRecipe.objects.filter(
            recipe__shopping_cart_recipe__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(sum_amount=Sum('amount')).order_by('ingredient__name')

        pdf_ingredients_list = self.pdf_gen(ingredients_annotate)

        response = FileResponse(pdf_ingredients_list,
                                as_attachment=True,
                                filename='shopping_cart.pdf')
        return response

    @action(methods=['POST', 'DELETE'], detail=True)
    def shopping_cart(self, request, pk):
        """
        Method for adding and deleting recipes to user's shopping cart.
        """
        if request.method == 'POST':
            return self.add_recipe(ShoppingCartSerializer, request, pk)
        return self.delete_recipe(ShoppingCart, request, pk)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Class for viewing tags.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Class for viewing ingredients.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
