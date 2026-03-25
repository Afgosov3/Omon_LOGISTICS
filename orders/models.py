import uuid
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import models

from clients.models import Client
from common.models import TimeStampedBaseModel
from drivers.models import Driver
from vehicles.models import Vehicle


def generate_order_id() -> str:
    return f"OM-{uuid.uuid4().hex[:8].upper()}"


class OrderStatus(models.TextChoices):
    NEW = "new", "New"
    CLIENT_CONFIRMED = "client_confirmed", "Client confirmed"
    DRIVER_SEARCH = "driver_search", "Driver search"
    DRIVER_ASSIGNED = "driver_assigned", "Driver assigned"
    ON_THE_WAY_TO_PICKUP = "on_the_way_to_pickup", "On the way to pickup"
    AT_PICKUP_LOCATION = "at_pickup_location", "At pickup location"
    LOADED = "loaded", "Loaded"
    ON_THE_WAY_WITH_CARGO = "on_the_way_with_cargo", "On the way with cargo"
    AT_DROPOFF_LOCATION = "at_dropoff_location", "At dropoff location"
    UNLOADING_REQUESTED = "unloading_requested", "Unloading requested"
    UNLOADING_CONFIRMED = "unloading_confirmed", "Unloading confirmed"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class Order(TimeStampedBaseModel):
    public_id = models.CharField(max_length=32, unique=True, default=generate_order_id)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="orders")
    created_by_dispatcher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_orders",
    )
    assigned_dispatcher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_orders",
    )
    assigned_driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    assigned_vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )

    cargo_name = models.CharField(max_length=255)
    cargo_description = models.TextField(blank=True)
    cargo_weight_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cargo_volume_m3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cargo_category = models.CharField(max_length=100, blank=True)

    client_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    driver_price = models.DecimalField(max_digits=12, decimal_places=2)

    current_status = models.CharField(
        max_length=64,
        choices=OrderStatus.choices,
        default=OrderStatus.NEW,
    )

    internal_comment = models.TextField(blank=True)

    is_cancelled = models.BooleanField(default=False)
    cancelled_reason = models.TextField(blank=True)

    completed_at = models.DateTimeField(null=True, blank=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    driver_assigned_at = models.DateTimeField(null=True, blank=True)
    estimated_distance_km = models.FloatField(null=True, blank=True)
    estimated_duration_minutes = models.IntegerField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["current_status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["assigned_driver"]),
            models.Index(fields=["client"]),
        ]

    def _validate_status_transition(self, old_status: str, new_status: str):
        if old_status == new_status:
            return
        allowed = ALLOWED_TRANSITIONS.get(old_status, [])
        if old_status and new_status not in allowed:
            raise ValidationError(
                {"current_status": f"Invalid transition from {old_status} to {new_status}"}
            )

    def save(self, *args, **kwargs):
        if self.pk:
            old = Order.objects.get(pk=self.pk)
            self._validate_status_transition(old.current_status, self.current_status)
        super().save(*args, **kwargs)


class OrderPointType(models.TextChoices):
    PICKUP = "pickup", "Pickup"
    WAYPOINT = "waypoint", "Waypoint"
    DROPOFF = "dropoff", "Dropoff"


class OrderPoint(TimeStampedBaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="points")
    point_type = models.CharField(max_length=16, choices=OrderPointType.choices)
    sequence = models.PositiveIntegerField()
    address = models.CharField(max_length=500)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    contact_person = models.CharField(max_length=255, blank=True)
    contact_phone = models.CharField(max_length=32, blank=True)

    class Meta:
        ordering = ["sequence"]
        unique_together = ["order", "sequence"]


class OrderStatusHistory(TimeStampedBaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="status_history")
    old_status = models.CharField(max_length=64, choices=OrderStatus.choices, null=True, blank=True)
    new_status = models.CharField(max_length=64, choices=OrderStatus.choices)
    changed_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_status_changes",
    )
    changed_by_driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_status_changes",
    )
    changed_by_system = models.BooleanField(default=False)
    actor_role = models.CharField(max_length=64, blank=True)
    comment = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["new_status"]),
        ]


class ProofKind(models.TextChoices):
    VIDEO = "video", "Video"
    CIRCLE_VIDEO = "circle_video", "Circle video"
    IMAGE = "image", "Image"
    DOCUMENT = "document", "Document"


class OrderProof(TimeStampedBaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="proofs")
    status_history = models.ForeignKey(
        OrderStatusHistory,
        on_delete=models.CASCADE,
        related_name="proofs",
    )
    uploaded_by_driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_proofs",
    )
    uploaded_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_proofs",
    )
    file = models.FileField(upload_to="order_proofs/")
    file_type = models.CharField(max_length=50, blank=True)
    mime_type = models.CharField(max_length=100, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    proof_kind = models.CharField(max_length=20, choices=ProofKind.choices)
    comment = models.TextField(blank=True)


ALLOWED_TRANSITIONS = {
    "new": ["client_confirmed"],
    "client_confirmed": ["driver_search"],
    "driver_search": ["driver_assigned"],
    "driver_assigned": ["on_the_way_to_pickup"],
    "on_the_way_to_pickup": ["at_pickup_location"],
    "at_pickup_location": ["loaded"],
    "loaded": ["on_the_way_with_cargo"],
    "on_the_way_with_cargo": ["at_dropoff_location"],
    "at_dropoff_location": ["unloading_requested"],
    "unloading_requested": ["unloading_confirmed"],
    "unloading_confirmed": ["completed"],
}
