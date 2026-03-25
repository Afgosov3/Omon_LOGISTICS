from django.db import models

from common.models import TimeStampedBaseModel


class BotSession(TimeStampedBaseModel):
    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    role = models.CharField(max_length=32)
    state = models.CharField(max_length=255, blank=True)
    payload_json = models.JSONField(default=dict, blank=True)
