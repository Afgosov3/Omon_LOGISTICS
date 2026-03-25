from django.conf import settings
from django.db import models

from common.models import TimeStampedBaseModel
from drivers.models import Driver
from orders.models import Order


class PayoutStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    CANCELLED = "cancelled", "Cancelled"


class PaymentMethod(models.TextChoices):
    BANK_TRANSFER = "bank_transfer", "Bank transfer"
    CASH = "cash", "Cash"
    OTHER = "other", "Other"


class Payout(TimeStampedBaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payouts")
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="payouts")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=16, choices=PayoutStatus.choices, default=PayoutStatus.PENDING)
    payment_method = models.CharField(
        max_length=32,
        choices=PaymentMethod.choices,
        default=PaymentMethod.BANK_TRANSFER,
    )
    paid_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="paid_payouts",
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    card_mask = models.CharField(max_length=32, blank=True)
    receipt_file = models.FileField(upload_to="payout_receipts/", null=True, blank=True)
    comment = models.TextField(blank=True)

    class Meta:
        unique_together = ["order"]
