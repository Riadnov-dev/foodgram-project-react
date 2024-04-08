from rest_framework import serializers
from .models import Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']

    def validate_color(self, value):
        if Tag.objects.filter(color=value).exists():
            raise serializers.ValidationError("Этот цвет уже занят")
        return value
