from django_filters import rest_framework as filters

from .models import Recipe


class RecipeFilter(filters.FilterSet):
    author = filters.NumberFilter(field_name='author__id')
    ingredients = filters.CharFilter(method='filter_by_ingredients')

    class Meta:
        model = Recipe
        fields = ['author', 'ingredients']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
