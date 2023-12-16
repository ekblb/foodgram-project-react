from colorfield import fields
from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from foodgram.constants import (MAX_LENGHT_COLOR, MAX_LENGHT_MEASUREMENT,
                                MAX_LENGHT_NAME, MAX_LENGHT_SLUG)

CustomUser = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        unique=True,
        max_length=MAX_LENGHT_NAME)
    color = fields.ColorField(
        verbose_name='Цвет в HEX',
        unique=True,
        max_length=MAX_LENGHT_COLOR)
    slug = models.SlugField(
        verbose_name='Уникальный слаг',
        unique=True,
        max_length=MAX_LENGHT_SLUG)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGHT_NAME)
    measurement_unit = models.CharField(
        verbose_name='Измеряемая единица',
        max_length=MAX_LENGHT_MEASUREMENT)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [models.UniqueConstraint(
            fields=['name', 'measurement_unit'],
            name='unique_name_measurement_unit')]

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        verbose_name='Автор рецепта',
        related_name='recipe_author',
        on_delete=models.CASCADE)
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGHT_NAME)
    image = models.ImageField(
        verbose_name='Картинка')
    text = models.CharField(
        verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Список ингредиентов',
        related_name='recipe_ingredients')
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Список тегов',
        related_name='recipe_tags')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (мин.)',
        validators=[MinValueValidator(
            limit_value=1,
            message='Значение не может быть меньше 1 мин.'),
            MaxValueValidator(
                limit_value=200,
                message='Значение не может быть больше 200 мин.')])
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date', 'name')

    def __str__(self) -> str:
        return self.name


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='recipe_ingredients',
        on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент в рецепте',
        related_name='ingredient_in_recipe',
        on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        verbose_name='Количество')

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        ordering = ('recipe', 'ingredient')
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'ingredient'],
            name='unique_recipe_ingredient')]

    def __str__(self) -> str:
        return f'{self.recipe} - {self.ingredient}'


class FavoriteRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='favorite_recipe',
        on_delete=models.CASCADE)
    user = models.ForeignKey(
        CustomUser,
        verbose_name='Пользователь',
        related_name='favorite_user',
        on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'user'],
            name='unique_favorite_recipe')]

    def __str__(self) -> str:
        return f'{self.user} - {self.recipe}'


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='shopping_cart_recipe',
        on_delete=models.CASCADE)
    user = models.ForeignKey(
        CustomUser,
        verbose_name='Пользователь',
        related_name='shopping_cart_user',
        on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'user'],
            name='unique_shopping_cart_recipe')]

    def __str__(self) -> str:
        return f'{self.user} - {self.recipe}'
