from django.db import models
from users.models import CustomUser

from .constants import MAX_LENGHT, MAX_LENGHT_COLOR


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        unique=True,
        max_length=MAX_LENGHT, )
    color = models.CharField(
        verbose_name='Цвет в HEX',
        unique=True,
        max_length=MAX_LENGHT_COLOR, )
    slug = models.SlugField(
        verbose_name='Уникальный слаг',
        unique=True,
        max_length=MAX_LENGHT,)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('id',)

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGHT,)
    measurement_unit = models.CharField(
        verbose_name='Измеряемая единица',
        max_length=MAX_LENGHT,)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('id',)

    def __str__(self) -> str:
        return f'{self.name}'


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент в рецепте',
        related_name='ingredient_in_recipe',
        on_delete=models.CASCADE,)
    amount = models.PositiveIntegerField(
        verbose_name='Количество',)

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        ordering = ('id',)

    def __str__(self) -> str:
        return f'{self.ingredient}'


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        verbose_name='Автор рецепта',
        related_name='recipe_author',
        on_delete=models.CASCADE,)
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGHT,)
    image = models.ImageField(
        verbose_name='Картинка',)
    text = models.CharField(
        verbose_name='Описание',
        max_length=MAX_LENGHT,)
    ingredients = models.ManyToManyField(
        IngredientInRecipe,
        verbose_name='Список ингредиентов',
        related_name='recipe_ingredients',)
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Список тегов',
        related_name='recipe_tags',)
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (мин.)',)
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return f'{self.name}'


class FavoriteRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='favorite_recipe',
        on_delete=models.CASCADE,)
    user = models.ForeignKey(
        CustomUser,
        verbose_name='Пользователь',
        related_name='favorite_user',
        on_delete=models.CASCADE,)

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorite_recipe'
            )
        ]

    def __str__(self) -> str:
        return f'{self.recipe}'


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='shopping_cart_recipe',
        on_delete=models.CASCADE,)
    user = models.ForeignKey(
        CustomUser,
        verbose_name='Пользователь',
        related_name='shopping_cart_user',
        on_delete=models.CASCADE,)

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_shopping_cart_recipe'
            )
        ]

    def __str__(self) -> str:
        return f'{self.recipe}'
