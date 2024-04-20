from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator, MaxLengthValidator
from rest_framework import serializers

from .models import UserFollow
from recipes.models import Recipe

MAX_LENGTH = 150

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed']

    def get_is_subscribed(self, obj):
        request_user = self.context.get('request').user
        return (UserFollow.objects.filter(user_from=request_user, user_to=obj
                                          ).exists() if request_user
                                           .is_authenticated else False)


class UserFollowSerializer(serializers.ModelSerializer):
    user_to = serializers.SlugRelatedField(slug_field='username',
                                           queryset=User.objects.all())

    class Meta:
        model = UserFollow
        fields = ['id', 'user_from', 'user_to', 'created']

    def create(self, validated_data):
        user_from = self.context['request'].user
        user_to = validated_data['user_to']
        follow, created = UserFollow.objects.get_or_create(user_from=user_from,
                                                           user_to=user_to)
        return follow


class CustomUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True,
                                     validators=[validate_password,
                                                 MaxLengthValidator(150)])
    first_name = serializers.CharField(required=True, max_length=MAX_LENGTH)
    last_name = serializers.CharField(required=True, max_length=MAX_LENGTH)
    username = serializers.CharField(
        required=True,
        max_length=MAX_LENGTH,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+\Z',
            message="Username must consist of letters, digits, or @/./+/-/_."
        )]
    )

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'first_name',
                  'last_name']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken."
                                              )
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user


class RecipeBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class UserSubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email',
                  'is_subscribed', 'recipes_count', 'recipes']

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit')
        recipes_qs = obj.recipes.all()
        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
                recipes_qs = recipes_qs[:recipes_limit]
            except ValueError:
                pass
        context = self.context.copy()
        return (RecipeBriefSerializer(recipes_qs, many=True, context=context)
                .data)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return UserFollow.objects.filter(user_from=request.user,
                                             user_to=obj).exists()
        return False

    def get_recipes_count(self, obj):
        return obj.recipes.count()
