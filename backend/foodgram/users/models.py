from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import Q, F


from .constants import MAX_LENGHT, MAX_LENGHT_EMAIL


class CustomUser(AbstractUser):

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=MAX_LENGHT_EMAIL,
        unique=True)
    username = models.CharField(
        verbose_name='Username',
        max_length=MAX_LENGHT,
        unique=True,
        validators=UnicodeUsernameValidator())
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_LENGHT)
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_LENGHT)
    password = models.CharField(
        verbose_name='Пароль',
        max_length=MAX_LENGHT)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['id']


class Subscription(models.Model):
    author = models.ForeignKey(
        CustomUser,
        verbose_name='Автор рецепта',
        related_name='subscription_author',
        on_delete=models.CASCADE)
    user = models.ForeignKey(
        CustomUser,
        verbose_name='Подписчик',
        related_name='subscription_user',
        on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_subscription'),
            models.CheckConstraint(
                check=Q(F('author') != F('user')),
                name='myself_subscription')]

    def __str__(self) -> str:
        return f'{self.author.username}'
