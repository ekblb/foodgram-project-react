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
            for row in file_reader:
                Ingredient.objects.bulk_create(Ingredient(**row))
