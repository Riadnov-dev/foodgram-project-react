from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend

from .models import Ingredient
from .serializers import IngredientSerializer
from .filters import IngredientFilter


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend,]
    pagination_class = None
    search_fields = ['^name',]
    filterset_class = IngredientFilter
