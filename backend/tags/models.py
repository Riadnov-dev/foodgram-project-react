from django.db import models

from .validators import validate_color

MAX_LENGTH_NAME = 100
MAX_LENGTH_COLOR = 7


class Tag(models.Model):
    name = models.CharField(max_length=MAX_LENGTH_NAME, unique=True)
    color = models.CharField(max_length=MAX_LENGTH_COLOR,
                             unique=True,
                             validators=[validate_color])
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name
