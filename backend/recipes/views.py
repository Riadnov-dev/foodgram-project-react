from django.db.models import Prefetch
from django.http import HttpResponse

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from .filters import RecipeFilter
from .models import Recipe, ShoppingList, Favorite, RecipeIngredient
from .permissions import IsOwnerOrReadOnly
from .serializers import RecipeSerializer, SimpleRecipeSerializer
from .pagination import LimitPageNumberPagination


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_context(self):
        context = super(RecipeViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset().order_by('-created_at'
                                                   ).prefetch_related(
            Prefetch(
                'recipe_ingredients',
                queryset=RecipeIngredient.objects.select_related('ingredient'))
        )
        tag_slugs = self.request.query_params.getlist('tags')
        if tag_slugs:
            queryset = queryset.filter(tags__slug__in=tag_slugs).distinct()
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')

        if user.is_authenticated:
            if is_favorited is not None:
                if is_favorited.lower() in ['true', '1']:
                    queryset = queryset.filter(in_favorites__user=user)
                else:
                    queryset = queryset.exclude(in_favorites__user=user)
            if is_in_shopping_cart is not None:
                if is_in_shopping_cart.lower() in ['true', '1']:
                    queryset = queryset.filter(in_shopping_list__user=user)
                else:
                    queryset = queryset.exclude(in_shopping_list__user=user)
        else:
            if is_favorited in ['0', '1'] or is_in_shopping_cart in ['0', '1']:
                pass

        return queryset.distinct()

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        elif self.action in ['create']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request, *args, **kwargs):
        shopping_list_items = (ShoppingList.objects.filter(user=request.user)
                               .select_related('recipe')
                               .prefetch_related('recipe__recipe_ingredients'))
        ingredients = {}

        for item in shopping_list_items:
            for recipe_ingredient in item.recipe.recipe_ingredients.all():
                ingredient = recipe_ingredient.ingredient
                amount = recipe_ingredient.amount
                if ingredient.name not in ingredients:
                    ingredients[ingredient.name] = {
                        'amount': amount,
                        'measurement_unit': ingredient.measurement_unit}
                else:
                    ingredients[ingredient.name]['amount'] += amount

        content = "\n".join([
            f"{name} - {info['amount']} "
            f"{info['measurement_unit']}"
            for name, info in ingredients.items()
        ])
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"')
        return response


class ShoppingCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, recipe_pk=None):
        try:
            recipe = Recipe.objects.get(pk=recipe_pk)
        except Recipe.DoesNotExist:
            return Response({'detail': 'Recipe does not exist.'},
                            status=status.HTTP_400_BAD_REQUEST)

        shopping_list_item, created = ShoppingList.objects.get_or_create(
            user=request.user, recipe=recipe)

        if created:
            serializer = SimpleRecipeSerializer(recipe,
                                                context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': 'Already in shopping cart'},
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, recipe_pk=None):
        try:
            recipe = Recipe.objects.get(pk=recipe_pk)
        except Recipe.DoesNotExist:
            return Response({'detail': 'Recipe does not exist.'},
                            status=status.HTTP_400_BAD_REQUEST)

        shopping_list_item = ShoppingList.objects.filter(user=request.user,
                                                         recipe=recipe)
        if shopping_list_item.exists():
            shopping_list_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'detail': 'Recipe was not in shopping cart'},
                            status=status.HTTP_400_BAD_REQUEST)


class FavoriteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, recipe_pk=None):
        try:
            recipe = Recipe.objects.get(pk=recipe_pk)
        except Recipe.DoesNotExist:
            return Response({'detail': 'Recipe does not exist.'},
                            status=status.HTTP_400_BAD_REQUEST)

        favorite_item, created = Favorite.objects.get_or_create(
            user=request.user, recipe=recipe)

        if created:
            serializer = SimpleRecipeSerializer(recipe,
                                                context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': 'Already in favorites'},
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, recipe_pk=None):
        try:
            recipe = Recipe.objects.get(pk=recipe_pk)
        except Recipe.DoesNotExist:
            return Response({'detail': 'Recipe does not exist.'},
                            status=status.HTTP_400_BAD_REQUEST)

        favorite_item = Favorite.objects.filter(user=request.user,
                                                recipe=recipe)
        if favorite_item.exists():
            favorite_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'detail': 'Recipe was not in favorites'},
                            status=status.HTTP_400_BAD_REQUEST)
