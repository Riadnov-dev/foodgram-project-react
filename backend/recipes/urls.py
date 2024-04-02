from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, ShoppingCartView, FavoriteView


router = DefaultRouter()
router.register('', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('<int:recipe_pk>/shopping_cart/',
         ShoppingCartView.as_view(),
         name='shopping_cart'),
    path('<int:recipe_pk>/favorite/',
         FavoriteView.as_view(),
         name='favorite'),
]
