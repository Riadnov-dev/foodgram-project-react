from django.db.models import Prefetch, Sum
from django.http import HttpResponse

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
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
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_context(self):
        context = super(RecipeViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_queryset(self):
        queryset = super().get_queryset().order_by('id').prefetch_related(
            Prefetch(
                'recipe_ingredients',
                queryset=RecipeIngredient.objects.select_related('ingredient')
            )
        )
        queryset = self.filter_by_tags(queryset)
        return self.filter_by_favorites_and_cart(queryset)

    def filter_by_tags(self, queryset):
        tag_slugs = self.request.query_params.getlist('tags')
        if tag_slugs:
            queryset = queryset.filter(tags__slug__in=tag_slugs).distinct()
        return queryset

    def filter_by_favorites_and_cart(self, queryset):
        user = self.request.user
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')

        if user.is_authenticated:
            if is_favorited:
                if is_favorited == '1':
                    queryset = queryset.filter(in_favorites__user=user)
                elif is_favorited == '0':
                    queryset = queryset.exclude(in_favorites__user=user)
            if is_in_shopping_cart:
                if is_in_shopping_cart == '1':
                    queryset = queryset.filter(in_shopping_list__user=user)
                elif is_in_shopping_cart == '0':
                    queryset = queryset.exclude(in_shopping_list__user=user)
        elif is_favorited == '1' or is_in_shopping_cart == '1':
            queryset = queryset.none()
        return queryset.distinct()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        elif self.action in ['create']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrReadOnly]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(
            detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request, *args, **kwargs):
        shopping_list_items = ShoppingList.objects.filter(user=request.user)
        ingredients = shopping_list_items.values(
            'recipe__recipe_ingredients__ingredient__name',
            'recipe__recipe_ingredients__ingredient__measurement_unit'
        ).annotate(total_amount=Sum('recipe__recipe_ingredients__amount'))

        content = "\n".join([
            "{} - {} {}".format(
                item['recipe__recipe_ingredients__ingredient__name'],
                item['total_amount'],
                item[
                    'recipe__recipe_ingredients__ingredient__measurement_unit'
                    ]
            )
            for item in ingredients
        ])

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"')
        return response


def validate_pk(pk):
    try:
        return int(pk)
    except ValueError:
        raise ValidationError('Invalid ID format. ID must be an integer.')


class ShoppingCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, recipe_pk=None):
        try:
            pk = validate_pk(recipe_pk)
            recipe = Recipe.objects.get(pk=pk)
        except ValidationError as e:
            return Response({'detail': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
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
            pk = validate_pk(recipe_pk)
            recipe = Recipe.objects.get(pk=pk)
        except ValidationError as e:
            return Response({'detail': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
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
            pk = validate_pk(recipe_pk)
            recipe = Recipe.objects.get(pk=pk)
        except ValidationError as e:
            return Response({'detail': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
        except Recipe.DoesNotExist:
            return Response({'detail': 'Recipe does not exist.'},
                            status=status.HTTP_400_BAD_REQUEST)

        favorite_item, created = Favorite.objects.get_or_create(
            user=request.user,
            recipe=recipe)

        if created:
            serializer = SimpleRecipeSerializer(recipe,
                                                context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': 'Already in favorites'},
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, recipe_pk=None):
        try:
            pk = validate_pk(recipe_pk)
            recipe = Recipe.objects.get(pk=pk)
        except ValidationError as e:
            return Response({'detail': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
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
