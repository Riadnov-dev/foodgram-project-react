from django.contrib import admin
from django.db.models import Count

from .models import Recipe, RecipeIngredient, ShoppingList, Favorite


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "favorites_count", "cooking_time")
    list_filter = ("author", "tags")
    search_fields = ("name", "author__username", "tags__name")
    inlines = [RecipeIngredientInline]
    autocomplete_fields = ["tags", "author"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(_favorites_count=Count("in_favorites"))
        return queryset

    def favorites_count(self, obj):
        return obj._favorites_count

    favorites_count.admin_order_field = "_favorites_count"


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("recipe", "ingredient", "amount")
    list_filter = ("recipe", "ingredient")
    search_fields = ("recipe__name", "ingredient__name")


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe", "added_at")
    list_filter = ("user",)
    search_fields = ("user__username", "recipe__name")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe", "added_at")
    list_filter = ("user",)
    search_fields = ("user__username", "recipe__name")
