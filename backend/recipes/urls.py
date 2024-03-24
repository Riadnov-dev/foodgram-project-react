from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import RecipeViewSet, ShoppingListViewSet, FavoriteViewSet

# Создаем роутер для рецептов
router = DefaultRouter()
router.register('', RecipeViewSet, basename='recipes')

# Создаем вложенный роутер для списка покупок
shopping_cart_router = routers.NestedSimpleRouter(router, r'', lookup='recipe')
shopping_cart_router.register(r'shopping_cart', ShoppingListViewSet, basename='shopping_cart')

# Создаем вложенный роутер для избранного
favorite_router = routers.NestedSimpleRouter(router, r'', lookup='recipe')
favorite_router.register(r'favorite', FavoriteViewSet, basename='favorite')

# Объединяем маршруты
urlpatterns = [
    path('', include(router.urls)),
    path('', include(shopping_cart_router.urls)),
    path('', include(favorite_router.urls)),
]
