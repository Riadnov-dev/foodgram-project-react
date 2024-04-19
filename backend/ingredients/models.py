from django.db import models

MAX_LENGTH_NAME = 200
MAX_LENGTH_MEASUREMENT_UNIT = 50


class Ingredient(models.Model):
    name = models.CharField(max_length=MAX_LENGTH_NAME)
    measurement_unit = models.CharField(max_length=MAX_LENGTH_MEASUREMENT_UNIT)

    class Meta:
        unique_together = ('name', 'measurement_unit')

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"
