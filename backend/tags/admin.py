from django.contrib import admin

from .models import Tag
from .forms import TagForm


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    form = TagForm
    list_display = ('name', 'color', 'slug',)
    search_fields = ('name',)
    ordering = ('name',)
