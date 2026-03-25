from rest_framework import serializers

from drivers.serializers import DriverSerializer
from .models import Payout


class PayoutSerializer(serializers.ModelSerializer):
    driver_details = DriverSerializer(source="driver", read_only=True)
    paid_by_name = serializers.CharField(source="paid_by_user.get_full_name", read_only=True)
    order_number = serializers.CharField(source="order.public_id", read_only=True)

    class Meta:
        model = Payout
        fields = [
            "id",
            "order",
            "order_number",
            "driver",
            "driver_details",
            "amount",
            "status",
            "payment_method",
            "paid_by_user",
            "paid_by_name",
            "paid_at",
            "card_mask",
            "receipt_file",
            "comment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "paid_by_user",
            "paid_at",
            "created_at",
            "updated_at",
            "status",
        ]

