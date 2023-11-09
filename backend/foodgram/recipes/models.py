from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from colorfield.fields import ColorField

from .constants import (MAX_LENGHT, MAX_COOKING_TIME, MIN_COOKING_TIME,
                        MIN_AMOUNT, MAX_AMOUNT)

CustomUser = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        unique=True,
        max_length=MAX_LENGHT)
    color = ColorField(
        verbose_name='Цвет в HEX')
    slug = models.SlugField(
        verbose_name='Уникальный слаг',
        unique=True,
        max_length=MAX_LENGHT)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGHT)
    measurement_unit = models.CharField(
        verbose_name='Измеряемая единица',
        max_length=MAX_LENGHT)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [models.UniqueConstraint(
            fields=['name', 'measurement_unit'],
            name='unique_name_measurement_unit')]

    def __str__(self) -> str:
        return f'{self.name}'


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        verbose_name='Рецепт',
        related_name='recipe_ingredient',
        on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент в рецепте',
        related_name='ingredient_in_recipe',
        on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(MIN_AMOUNT),
                    MaxValueValidator(MAX_AMOUNT)])

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        ordering = ('recipe',)
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'ingredient'],
            name='unique_recipe_ingredient')]

    def __str__(self) -> str:
        return f'{self.ingredient, self.amount}'


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        verbose_name='Автор рецепта',
        related_name='recipe_author',
        on_delete=models.CASCADE)
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGHT)
    image = models.ImageField(
        verbose_name='Картинка')
    text = models.CharField(
        verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through=IngredientInRecipe,
        verbose_name='Список ингредиентов',
        related_name='recipe_ingredients')
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Список тегов',
        related_name='recipe_tags')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (мин.)',
        validators=[MinValueValidator(MIN_COOKING_TIME),
                    MaxValueValidator(MAX_COOKING_TIME)])
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return f'{self.name}'


class CategoryRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE)
    user = models.ForeignKey(
        CustomUser,
        verbose_name='Пользователь',
        on_delete=models.CASCADE)

    class Meta:
        ordering = ('recipe',)
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'user'],
            name='unique_category_recipe')]

    def __str__(self) -> str:
        return f'{self.recipe}'


class FavoriteRecipe(CategoryRecipe):
    recipe = models.ForeignKey(related_name='favorite_recipe')
    user = models.ForeignKey(related_name='favorite_user')

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingCart(CategoryRecipe):
    recipe = models.ForeignKey(related_name='shopping_cart_recipe')
    user = models.ForeignKey(related_name='shopping_cart_user')

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
