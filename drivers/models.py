from django.conf import settings
from django.db import models

from common.models import TimeStampedBaseModel


class Driver(TimeStampedBaseModel):
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=32)
    telegram_id = models.BigIntegerField(unique=True)
    telegram_username = models.CharField(max_length=255, blank=True)
    card_holder_name = models.CharField(max_length=255, blank=True)
    card_number_encrypted = models.CharField(max_length=512, blank=True)
    card_mask = models.CharField(max_length=32, blank=True)
    is_active = models.BooleanField(default=True)
    is_online = models.BooleanField(default=False)
    joined_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_drivers",
    )
    card_last4 = models.CharField(max_length=4, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Location tracking
    current_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_location_update = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["telegram_id"]),
            models.Index(fields=["phone"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return self.full_name
