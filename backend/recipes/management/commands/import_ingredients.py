import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Class for loading ingredients.csv to the database.
    """
    help = 'Load ingredients.csv to the database'

    def handle(self, *args, **options):
        with open('recipes/data/ingredients.csv', encoding='utf-8') as file:
            file_reader = csv.DictReader(file)
            Ingredient.objects.bulk_create(
                Ingredient(**data) for data in file_reader)
