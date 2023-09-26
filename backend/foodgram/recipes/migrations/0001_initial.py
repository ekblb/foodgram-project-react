# Generated by Django 4.2.5 on 2023-09-19 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredients',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название')),
                ('measurement_unit', models.CharField(max_length=200, verbose_name='Измеряемая единица')),
            ],
        ),
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Название')),
                ('color', models.CharField(blank=True, max_length=7, verbose_name='Цвет в HEX')),
                ('slug', models.SlugField(blank=True, max_length=200, null=True, unique=True, verbose_name='Уникальный слаг')),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='', verbose_name='Картинка')),
                ('name', models.CharField(max_length=200, verbose_name='Название')),
                ('text', models.CharField(max_length=200, verbose_name='Описание')),
                ('cooking_time', models.PositiveIntegerField(verbose_name='Время приготовления (мин.)')),
                ('ingredients', models.ManyToManyField(to='recipes.ingredients', verbose_name='Список ингредиентов')),
                ('tags', models.ManyToManyField(to='recipes.tags', verbose_name='Список id тегов')),
            ],
        ),
    ]
