import uuid
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from clients.models import Client
from common.models import TimeStampedBaseModel
from drivers.models import Driver
from vehicles.models import Vehicle


def generate_order_id() -> str:
    return f"OM-{uuid.uuid4().hex[:8].upper()}"


class OrderStatus(models.TextChoices):
    NEW = "new", _("Yangi")
    CLIENT_CONFIRMED = "client_confirmed", _("Mijoz tasdiqladi")
    DRIVER_SEARCH = "driver_search", _("Haydovchi qidirilmoqda")
    DRIVER_ASSIGNED = "driver_assigned", _("Haydovchi biriktirildi")
    ON_THE_WAY_TO_PICKUP = "on_the_way_to_pickup", _("Yuk olishga yo'lda")
    AT_PICKUP_LOCATION = "at_pickup_location", _("Yuk olish joyida")
    LOADED = "loaded", _("Yuk ortildi")
    ON_THE_WAY_WITH_CARGO = "on_the_way_with_cargo", _("Yuk bilan yo'lda")
    AT_DROPOFF_LOCATION = "at_dropoff_location", _("Tushirish joyida")
    UNLOADING_REQUESTED = "unloading_requested", _("Tushirish boshlandi")
    UNLOADING_CONFIRMED = "unloading_confirmed", _("Tushirish tasdiqlandi")
    COMPLETED = "completed", _("Yakunlangan")
    CANCELLED = "cancelled", _("Bekor qilingan")


class Order(TimeStampedBaseModel):
    public_id = models.CharField(max_length=32, unique=True, default=generate_order_id, verbose_name=_("Buyurtma kodi"))
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="orders", verbose_name=_("Mijoz"))
    created_by_dispatcher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_orders",
        verbose_name=_("Yaratgan dispatcher"),
    )
    assigned_dispatcher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_orders",
        verbose_name=_("Biriktirilgan dispatcher"),
    )
    assigned_driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name=_("Biriktirilgan haydovchi"),
    )
    assigned_vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name=_("Biriktirilgan transport"),
    )

    cargo_name = models.CharField(max_length=255, verbose_name=_("Yuk nomi"))
    cargo_description = models.TextField(blank=True, verbose_name=_("Yuk tavsifi"))
    cargo_weight_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Yuk vazni (kg)"))
    cargo_volume_m3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Yuk hajmi (m³)"))
    cargo_category = models.CharField(max_length=100, blank=True, verbose_name=_("Yuk toifasi"))

    client_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name=_("Mijoz narxi"))
    driver_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_("Haydovchi narxi"))

    current_status = models.CharField(
        max_length=64,
        choices=OrderStatus.choices,
        default=OrderStatus.NEW,
        verbose_name=_("Joriy holat"),
    )

    internal_comment = models.TextField(blank=True, verbose_name=_("Ichki izoh"))

    is_cancelled = models.BooleanField(default=False, verbose_name=_("Bekor qilingan"))
    cancelled_reason = models.TextField(blank=True, verbose_name=_("Bekor qilish sababi"))

    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Yakunlangan vaqt"))
    assigned_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Biriktirilgan vaqt"))
    driver_assigned_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Haydovchi biriktirilgan vaqt"))
    estimated_distance_km = models.FloatField(null=True, blank=True, verbose_name=_("Taxminiy masofa (km)"))
    estimated_duration_minutes = models.IntegerField(null=True, blank=True, verbose_name=_("Taxminiy davomiylik (daq)"))
    is_deleted = models.BooleanField(default=False, verbose_name=_("O'chirilgan"))
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name=_("O'chirilgan vaqt"))

    class Meta:
        indexes = [
            models.Index(fields=["current_status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["assigned_driver"]),
            models.Index(fields=["client"]),
        ]
        verbose_name = _("Buyurtma")
        verbose_name_plural = _("Buyurtmalar")

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
    PICKUP = "pickup", _("Yuk olish")
    WAYPOINT = "waypoint", _("Oraliq nuqta")
    DROPOFF = "dropoff", _("Tushirish")


class OrderPoint(TimeStampedBaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="points", verbose_name=_("Buyurtma"))
    point_type = models.CharField(max_length=16, choices=OrderPointType.choices, verbose_name=_("Nuqta turi"))
    sequence = models.PositiveIntegerField(verbose_name=_("Tartib raqami"))
    address = models.CharField(max_length=500, verbose_name=_("Manzil"))
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name=_("Kenglik"))
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name=_("Uzunlik"))
    contact_person = models.CharField(max_length=255, blank=True, verbose_name=_("Aloqa shaxsi"))
    contact_phone = models.CharField(max_length=32, blank=True, verbose_name=_("Telefon"))

    class Meta:
        ordering = ["sequence"]
        unique_together = ["order", "sequence"]
        verbose_name = _("Buyurtma nuqtasi")
        verbose_name_plural = _("Buyurtma nuqtalari")


class OrderStatusHistory(TimeStampedBaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="status_history", verbose_name=_("Buyurtma"))
    old_status = models.CharField(max_length=64, choices=OrderStatus.choices, null=True, blank=True, verbose_name=_("Eski holat"))
    new_status = models.CharField(max_length=64, choices=OrderStatus.choices, verbose_name=_("Yangi holat"))
    changed_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_status_changes",
        verbose_name=_("O'zgartirgan foydalanuvchi"),
    )
    changed_by_driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_status_changes",
        verbose_name=_("O'zgartirgan haydovchi"),
    )
    changed_by_system = models.BooleanField(default=False, verbose_name=_("Tizim tomonidan"))
    actor_role = models.CharField(max_length=64, blank=True, verbose_name=_("Rol"))
    comment = models.TextField(blank=True, verbose_name=_("Izoh"))

    class Meta:
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["new_status"]),
        ]
        verbose_name = _("Holat tarixi")
        verbose_name_plural = _("Holat tarixi yozuvlari")


class ProofKind(models.TextChoices):
    VIDEO = "video", _("Video")
    CIRCLE_VIDEO = "circle_video", _("Aylana video")
    IMAGE = "image", _("Rasm")
    DOCUMENT = "document", _("Hujjat")


class OrderProof(TimeStampedBaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="proofs", verbose_name=_("Buyurtma"))
    status_history = models.ForeignKey(
        OrderStatusHistory,
        on_delete=models.CASCADE,
        related_name="proofs",
        verbose_name=_("Holat tarixi"),
    )
    uploaded_by_driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_proofs",
        verbose_name=_("Haydovchi"),
    )
    uploaded_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_proofs",
        verbose_name=_("Foydalanuvchi"),
    )
    file = models.FileField(upload_to="order_proofs/", verbose_name=_("Fayl"))
    file_type = models.CharField(max_length=50, blank=True, verbose_name=_("Fayl turi"))
    mime_type = models.CharField(max_length=100, blank=True, verbose_name=_("MIME turi"))
    file_size = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Fayl hajmi (bayt)"))
    proof_kind = models.CharField(max_length=20, choices=ProofKind.choices, verbose_name=_("Isbot turi"))
    comment = models.TextField(blank=True, verbose_name=_("Izoh"))

    class Meta:
        verbose_name = _("Isbot")
        verbose_name_plural = _("Isbotlar")


ALLOWED_TRANSITIONS = {
    "new": ["client_confirmed", "on_the_way_to_pickup"],
    "client_confirmed": ["driver_search", "on_the_way_to_pickup"],
    "driver_search": ["driver_assigned", "on_the_way_to_pickup"],
    "driver_assigned": ["on_the_way_to_pickup"],
    "on_the_way_to_pickup": ["at_pickup_location"],
    "at_pickup_location": ["loaded"],
    "loaded": ["on_the_way_with_cargo"],
    "on_the_way_with_cargo": ["at_dropoff_location"],
    "at_dropoff_location": ["unloading_requested"],
    "unloading_requested": ["unloading_confirmed"],
    "unloading_confirmed": ["completed"],
}
