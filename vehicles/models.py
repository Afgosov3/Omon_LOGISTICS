from django.db import models

from common.models import TimeStampedBaseModel
from drivers.models import Driver


class Vehicle(TimeStampedBaseModel):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="vehicles")
    type = models.CharField(max_length=100)
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    plate_number = models.CharField(max_length=50)
    capacity_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    volume_m3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.plate_number} ({self.type})"
