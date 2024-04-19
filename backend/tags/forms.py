from django import forms
from django.core.exceptions import ValidationError

from .models import Tag
from .validators import validate_color


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = '__all__'

    def clean_color(self):
        color = self.cleaned_data.get('color')
        color = validate_color(color)
        if Tag.objects.filter(color=color
                              ).exclude(pk=self.instance.pk).exists():
            raise ValidationError('This color is already in use.')
        return color
