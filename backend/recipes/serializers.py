from rest_framework import serializers
from .models import (Recipe,
                     RecipeIngredient,
                     ShoppingList,
                     Favorite,
                     Tag,
                     Ingredient
                     )
from rest_framework import serializers
from django.db import transaction


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'amount', 'measurement_unit']


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(slug_field='slug', queryset=Tag.objects.all(), many=True)
    ingredients = RecipeIngredientSerializer(source='recipeingredient_set', many=True)
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'text', 'tags', 'ingredients', 'cooking_time', 'author']

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        with transaction.atomic():
            recipe = Recipe.objects.create(**validated_data)
            recipe.tags.set(tags_data)
            for ingredient_data in ingredients_data:
                RecipeIngredient.objects.create(recipe=recipe, **ingredient_data)
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', [])
        ingredients_data = validated_data.pop('ingredients', [])

        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.save()

        if tags_data:
            instance.tags.set(tags_data)
        
        if ingredients_data:
            instance.ingredients.clear()
            for ingredient_data in ingredients_data:
                ingredient, _ = Ingredient.objects.get_or_create(
                    name=ingredient_data['name'],
                    defaults={'measurement_unit': ingredient_data['measurement_unit']}
                )
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient,
                    amount=ingredient_data['amount']
                )

        return instance


class ShoppingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = ['id', 'user', 'recipe', 'added_at']


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'recipe', 'added_at']
