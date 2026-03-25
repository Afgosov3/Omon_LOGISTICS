from django.db import models

from common.models import TimeStampedBaseModel


class AuditLog(TimeStampedBaseModel):
    actor_type = models.CharField(max_length=32)
    actor_id = models.PositiveIntegerField(null=True, blank=True)
    action = models.CharField(max_length=255)
    entity_type = models.CharField(max_length=64)
    entity_id = models.PositiveIntegerField(null=True, blank=True)
    before_json = models.JSONField(null=True, blank=True)
    after_json = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
