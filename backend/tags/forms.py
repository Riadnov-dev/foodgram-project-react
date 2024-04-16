from django import forms
from django.core.exceptions import ValidationError
from .models import Tag
import re


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = '__all__'

    def clean_color(self):
        color = self.cleaned_data.get('color').lower()
        if not re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color):
            raise ValidationError(f'{color} is not a valid HEX color.')
        if Tag.objects.filter(color=color).exclude(pk=self.instance.pk
                                                   ).exists():
            raise ValidationError('This color is already in use.')
        return color
