# Generated by Django 4.2.5 on 2023-09-23 22:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_favorite_shoppingcart_subscription_ingredient_amount_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingredient',
            name='amount',
        ),
    ]
