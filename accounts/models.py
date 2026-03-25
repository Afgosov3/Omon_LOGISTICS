from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    MAIN_DISPATCHER = "main_dispatcher", "Main Dispatcher"
    DISPATCHER = "dispatcher", "Dispatcher"


class User(AbstractUser):
    """Custom user model for internal CRM users (dispatchers)."""

    email = models.EmailField("email address", unique=True)
    phone = models.CharField(max_length=32, blank=True)
    role = models.CharField(
        max_length=32,
        choices=UserRole.choices,
        default=UserRole.DISPATCHER,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return f"{self.get_full_name() or self.email} ({self.role})"
