from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

MAX_LENGTH = 150


class CustomUser(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(
        _("username"), max_length=MAX_LENGTH, unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    def __str__(self):
        return self.email


class UserFollow(models.Model):
    user_from = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="rel_from_set",
        on_delete=models.CASCADE
    )
    user_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="rel_to_set",
        on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-created",)
        unique_together = ("user_from", "user_to")

    def __str__(self):
        return f"{self.user_from} follows {self.user_to}"
