# Generated by Django 4.2.5 on 2023-12-13 09:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_customuser_options_alter_subscription_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'ordering': ('username',), 'verbose_name': 'Пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
        migrations.AlterModelOptions(
            name='subscription',
            options={'ordering': ('author', 'user'), 'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
    ]