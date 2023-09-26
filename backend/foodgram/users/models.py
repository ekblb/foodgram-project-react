from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
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
