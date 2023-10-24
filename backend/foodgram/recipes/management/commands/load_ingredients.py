import csv
from typing import Any

from django.core.management.base import BaseCommand
from models import Ingredient

from foodgram.settings import BASE_DIR


class Command(BaseCommand):
    help = 'Import json file with ingredients to table "recipes_ingredient"'

    def handle(self, *args: Any, **options: Any):
        with open(f'{BASE_DIR}/data/ingredients.json') as file:
            reader = csv.DictReader(file)
            Ingredient.objects.bulk_create(
                Ingredient(**data) for data in reader
            )
        self.stdout.write('Данные успешно загрузились')
