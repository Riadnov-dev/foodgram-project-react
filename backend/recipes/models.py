from django.db import models
from django.conf import settings

from ingredients.models import Ingredient
from tags.models import Tag

MAX_LENGTH = 200


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey('Recipe',
                               related_name='recipe_ingredients',
                               on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient,
                                   related_name='ingredient_recipes',
                                   on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.ingredient.name} in {self.recipe.name}"


class Recipe(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='recipes')
    name = models.CharField(max_length=MAX_LENGTH)
    image = models.ImageField(upload_to='recipes/')
    text = models.TextField()
    tags = models.ManyToManyField(Tag, related_name='recipes')
    cooking_time = models.PositiveIntegerField()
    ingredients = models.ManyToManyField(Ingredient,
                                         through=RecipeIngredient,
                                         related_name='recipes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ShoppingList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='shopping_list')
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE,
                               related_name='in_shopping_list')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')
        ordering = ['added_at']

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в список покупок'


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='favorites')
    recipe = models.ForeignKey('Recipe',
                               on_delete=models.CASCADE,
                               related_name='in_favorites')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')
        ordering = ['added_at']

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в избранное'
