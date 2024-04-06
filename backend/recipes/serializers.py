import base64
from django.db import transaction
from django.core.files.base import ContentFile

from rest_framework import serializers

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag,
)
from users.models import UserFollow


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    ingredients = RecipeIngredientSerializer(many=True, write_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'text', 'tags', 'ingredients',
                  'cooking_time', 'author',
                  'is_favorited', 'is_in_shopping_cart']

    def to_representation(self, instance):
        representation = (super(RecipeSerializer, self)
                          .to_representation(instance))
        ingredients_data = []
        for recipe_ingredient in instance.recipe_ingredients.all():
            ingredient_data = {
                'id': recipe_ingredient.ingredient.id,
                'name': recipe_ingredient.ingredient.name,
                'measurement_unit': (recipe_ingredient
                                     .ingredient
                                     .measurement_unit),
                'amount': recipe_ingredient.amount
            }
            ingredients_data.append(ingredient_data)
        representation['ingredients'] = ingredients_data

        tags_data = []
        for tag in instance.tags.all():
            tag_data = {
                'id': tag.id,
                'name': tag.name,
                'color': tag.color,
                'slug': tag.slug
            }
            tags_data.append(tag_data)
        representation['tags'] = tags_data

        return representation

    def get_is_favorited(self, obj):
        user = self.context['request'].user

        if user.is_authenticated:
            is_favorited = (Favorite.objects.filter(user=user, recipe=obj)
                            .exists())
            return is_favorited
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user

        if user.is_authenticated:
            is_in_shopping_cart = (ShoppingList.objects
                                   .filter(user=user, recipe=obj).exists())
            return is_in_shopping_cart
        return False

    def get_author(self, obj):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            is_subscribed = UserFollow.objects.filter(user_from=request.user,
                                                      user_to=obj.author
                                                      ).exists()
        else:
            is_subscribed = False
        return {
            "id": obj.author.id,
            "username": obj.author.username,
            "first_name": obj.author.first_name,
            "last_name": obj.author.last_name,
            "email": obj.author.email,
            "is_subscribed": is_subscribed
        }

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                "Необходимо указать хотя бы один тег.")
        tag_ids = [tag.id for tag in value]
        if len(tag_ids) != len(set(tag_ids)):
            raise serializers.ValidationError("Теги не могут повторяться.")
        if not Tag.objects.filter(id__in=tag_ids).count() == len(tag_ids):
            raise serializers.ValidationError(
                "Один или несколько предоставленных тегов не существуют.")
        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                "Список ингредиентов не может быть пустым.")
        ingredient_ids = [item['id'] for item in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                "Ингредиенты не могут повторяться.")
        validated_ingredients = []
        for ingredient_data in value:
            ingredient_id = ingredient_data['id']
            amount = ingredient_data['amount']
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(
                    f"Ингредиент с ID {ingredient_id} не существует.")
            if amount <= 0:
                raise serializers.ValidationError(
                    "Количество каждого ингредиента должно быть больше нуля.")
            validated_ingredients.append({'id': ingredient_id,
                                          'amount': amount})
        return validated_ingredients

    def validate(self, data):
        request = self.context.get('request')
        if request and request.method == 'PATCH':
            missing_fields = []
            if 'tags' not in request.data:
                missing_fields.append('tags')
            if 'ingredients' not in request.data:
                missing_fields.append('ingredients')

            if missing_fields:
                raise serializers.ValidationError(
                    {field: "Это поле обязательно."
                     for field in missing_fields})

        if 'cooking_time' in data and data['cooking_time'] < 1:
            raise serializers.ValidationError(
                {"cooking_time": "Время приготовления должно быть больше нуля"}
                )

        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_data['id'])
            amount = ingredient_data['amount']
            RecipeIngredient.objects.create(recipe=recipe,
                                            ingredient=ingredient,
                                            amount=amount)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.tags.clear()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        instance.tags.set(tags_data)
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_data['id'])
            amount = ingredient_data['amount']
            RecipeIngredient.objects.create(recipe=instance,
                                            ingredient=ingredient,
                                            amount=amount)

        return instance


class SimpleRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class ShoppingListSerializer(serializers.ModelSerializer):
    recipe = SimpleRecipeSerializer(read_only=True)

    class Meta:
        model = ShoppingList
        fields = ['recipe']


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'recipe', 'added_at']
