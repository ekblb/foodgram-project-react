from django.db import models
from users.models import CustomUser


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        )
    measurement_unit = models.CharField(
        verbose_name='Измеряемая единица',
        max_length=200,
        )
    # amount = models.PositiveIntegerField(
    #     verbose_name='Количество',
    # )

    def __str__(self) -> str:
        return f'{self.name}'


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

    def __str__(self) -> str:
        return self.name


def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.author.id, filename)


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        verbose_name='Автор публикации',
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
        )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Список id тегов',
        )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (мин.)',
        )

    def __str__(self) -> str:
        return self.name


class Favorite(models.Model):
    pass


class ShoppingCart(models.Model):
    pass


class Subscription(models.Model):
    pass
