from django.contrib import admin
from django.db.models import Count
from .models import Recipe, RecipeIngredient, ShoppingList, Favorite

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_count')
    
    def get_queryset(self, request):
        # Оптимизация запроса с подсчетом количества избранных через аннотацию
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(_favorites_count=Count('in_favorites'))
        return queryset

    def favorites_count(self, obj):
        # Возвращаем значение аннотированного поля
        return obj._favorites_count
    favorites_count.admin_order_field = '_favorites_count'

class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1

class ShoppingListInline(admin.TabularInline):
    model = ShoppingList
    extra = 0

class FavoriteInline(admin.TabularInline):
    model = Favorite
    extra = 0

@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')

@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'added_at')
    search_fields = ('user__username', 'recipe__name')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'added_at')
    search_fields = ('user__username', 'recipe__name')
