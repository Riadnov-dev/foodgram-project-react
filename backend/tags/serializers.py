from rest_framework import serializers

from .models import Tag
from .validators import validate_color


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']

    def validate_color(self, value):
        return validate_color(value)
