from rest_framework import viewsets, permissions, mixins, status, response, decorators
from rest_framework.viewsets import GenericViewSet
from django.shortcuts import get_object_or_404
from .models import Recipe, ShoppingList, Favorite
from .serializers import RecipeSerializer, FavoriteSerializer, ShoppingListSerializer
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.response import Response


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

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

    @decorators.action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request, *args, **kwargs):
        shopping_list_items = ShoppingList.objects.filter(user=request.user).prefetch_related('recipe__ingredients__ingredient')
        ingredients = {}

        for item in shopping_list_items:
            for recipeingredient in item.recipe.ingredients.all():
                ingredient_name = recipeingredient.ingredient.name
                amount = recipeingredient.amount
                measurement_unit = recipeingredient.ingredient.measurement_unit
                if ingredient_name not in ingredients:
                    ingredients[ingredient_name] = {'amount': amount, 'measurement_unit': measurement_unit}
                else:
                    ingredients[ingredient_name]['amount'] += amount

        content = "\n".join([
            f"{ingredient} - {details['amount']} {details['measurement_unit']}"
            for ingredient, details in ingredients.items()
        ])
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response


class FavoriteViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      GenericViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user, recipe__id=self.kwargs['recipe_pk'])

    @action(methods=['post'], detail=True, permission_classes=[permissions.IsAuthenticated])
    def add(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        favorite, created = Favorite.objects.get_or_create(user=request.user, recipe=recipe)
        if created:
            return Response({'status': 'Added to favorites'})
        else:
            return Response({'status': 'Already in favorites'}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['delete'], detail=True, permission_classes=[permissions.IsAuthenticated])
    def remove(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        affected_rows = Favorite.objects.filter(user=request.user, recipe=recipe).delete()
        if affected_rows:
            return Response({'status': 'Removed from favorites'})
        else:
            return Response({'status': 'Recipe was not in favorites'}, status=status.HTTP_400_BAD_REQUEST)


class ShoppingListViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = ShoppingList.objects.filter(user=request.user).prefetch_related('recipe__ingredients')
        serializer = ShoppingListSerializer(queryset, many=True)
        return response.Response(serializer.data)

    @action(methods=['post'], detail=True)
    def add_to_cart(self, request, *args, **kwargs):
        recipe_pk = kwargs.get('pk') 
        recipe = get_object_or_404(Recipe, pk=recipe_pk)
        _, created = ShoppingList.objects.get_or_create(user=request.user, recipe=recipe)
        if created:
            return response.Response({'status': 'Added to shopping cart'})
        else:
            return response.Response({'status': 'Already in shopping cart'}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['delete'], detail=True)
    def remove_from_cart(self, request, *args, **kwargs):
        recipe_pk = kwargs.get('pk')
        recipe = get_object_or_404(Recipe, pk=recipe_pk)
        affected_rows = ShoppingList.objects.filter(user=request.user, recipe=recipe).delete()
        if affected_rows[0] > 0:
            return response.Response({'status': 'Removed from shopping cart'})
        else:
            return response.Response({'status': 'Recipe was not in shopping cart'}, status=status.HTTP_400_BAD_REQUEST)
