from django.db import models
from users.models import CustomUser


def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.author.id, filename)


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        unique=True,
        max_length=200,
        )
    color = models.CharField(
        verbose_name='Цвет в HEX',
        unique=True,
        max_length=7,
        )
    slug = models.SlugField(
        verbose_name='Уникальный слаг',
        unique=True,
        max_length=200,
        )

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        )
    measurement_unit = models.CharField(
        verbose_name='Измеряемая единица',
        max_length=200,
        )

    def __str__(self) -> str:
        return f'{self.name}'


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        verbose_name='Автор публикации',
        related_name='recipes',
        on_delete=models.CASCADE,
        )
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to=user_directory_path,
        )
    text = models.CharField(
        verbose_name='Описание',
        max_length=200,
        )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Список ингредиентов',
        through='RecipeIngredients',
        through_fields=('recipe', 'ingredient',),
        )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Список тегов',
        )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (мин.)',
        )

    def __str__(self) -> str:
        return self.name


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Название рецепта',
        on_delete=models.CASCADE,
        )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент в рецепте',
        on_delete=models.CASCADE,
        )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'RecipeIngredient'
        verbose_name_plural = 'RecipeIngredients'

    def __str__(self) -> str:
        return f'{self.ingredient}'


class Favorite(models.Model):
    pass


class ShoppingCart(models.Model):
    pass


class Subscription(models.Model):
    pass
