from django.db import models

from common.models import TimeStampedBaseModel


class TargetType(models.TextChoices):
    CLIENT = "client", "Client"
    DRIVER = "driver", "Driver"
    USER = "user", "User"


class Channel(models.TextChoices):
    TELEGRAM = "telegram", "Telegram"
    CRM = "crm", "CRM"


class Notification(TimeStampedBaseModel):
    target_type = models.CharField(max_length=16, choices=TargetType.choices)
    target_id = models.PositiveIntegerField()
    channel = models.CharField(max_length=16, choices=Channel.choices)
    title = models.CharField(max_length=255)
    body = models.TextField()
    related_order_id = models.PositiveIntegerField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
