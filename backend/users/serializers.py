from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserFollow
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer


User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'is_subscribed']

    def get_is_subscribed(self, obj):
        request_user = self.context.get('request').user
        return UserFollow.objects.filter(user_from=request_user, user_to=obj).exists() if request_user.is_authenticated else False

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if not self.context.get('request').user.is_authenticated:
            ret.pop('is_subscribed', None)
        return ret


class UserFollowSerializer(serializers.ModelSerializer):
    user_to = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    class Meta:
        model = UserFollow
        fields = ['id', 'user_from', 'user_to', 'created']

    def create(self, validated_data):
        user_from = self.context['request'].user
        user_to = validated_data['user_to']
        follow, created = UserFollow.objects.get_or_create(user_from=user_from, user_to=user_to)
        return follow


class CustomUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+\Z',
            message="Username must consist of letters, digits, or @/./+/-/_ only."
        )]
    )

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'first_name', 'last_name']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
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
