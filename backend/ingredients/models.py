from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=50)

    class Meta:
        unique_together = ('name', 'measurement_unit')

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"
