from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        unique=True,
        )
    username = models.CharField(
        verbose_name='Username',
        max_length=150,
        unique=True,
        )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=150,
        )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Subscription(models.Model):
    author = models.ForeignKey(
        CustomUser,
        verbose_name='Автор рецепта',
        related_name='subscription_author',
        on_delete=models.CASCADE,
        )
    user = models.ForeignKey(
        CustomUser,
        verbose_name='Подписчик',
        related_name='subscription_user',
        on_delete=models.CASCADE,
        )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_subscribtion'
            )
        ]

    def __str__(self) -> str:
        return f'{self.author}'
