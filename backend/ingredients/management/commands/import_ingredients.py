import json
from django.core.management.base import BaseCommand, CommandError
from ingredients.models import Ingredient


class Command(BaseCommand):
    help = 'Imports ingredients from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file',
                            type=str,
                            help='The path to the JSON file.')

    def handle(self, *args, **options):
        try:
            with open(options['json_file'], 'r', encoding='utf-8') as jsonfile:
                data = json.load(jsonfile)
                for item in data:
                    Ingredient.objects.create(
                        name=item['name'],
                        measurement_unit=item['measurement_unit'])
                self.stdout.write(
                    self.style.SUCCESS('Successfully imported ingredients'))
        except Exception as e:
            raise CommandError(f'Error importing ingredients: {e}')
