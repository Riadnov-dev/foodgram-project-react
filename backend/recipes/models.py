from django.db import models
from django.conf import settings
from ingredients.models import Ingredient
from tags.models import Tag


class Recipe(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recipes')
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='recipes/')
    text = models.TextField()
    tags = models.ManyToManyField(Tag, related_name='recipes')
    cooking_time = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    @property
    def favorites_count(self):
        return self.in_favorites.count()


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='recipes')
    amount = models.PositiveIntegerField()

    class Meta:
        unique_together = ('recipe', 'ingredient')


class ShoppingList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shopping_list')
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE, related_name='in_shopping_list')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')
        ordering = ['added_at']

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в список покупок'


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE, related_name='in_favorites')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')
        ordering = ['added_at']

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в избранное'