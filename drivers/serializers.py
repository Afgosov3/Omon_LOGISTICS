from rest_framework import serializers
from .models import Driver

class DriverSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    active_orders_count = serializers.SerializerMethodField()

    class Meta:
        model = Driver
        fields = [
            "id",
            "full_name",
            "phone",
            "telegram_id",
            "telegram_username",
            "card_holder_name",
            "card_mask",
            "is_active",
            "is_online",
            "joined_at",
            "notes",
            "created_by",
            "created_by_name",
            "active_orders_count",
            "card_last4",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "joined_at",
            "created_at",
            "updated_at",
            "active_orders_count",
            "card_mask",
            "card_last4"
        ]
        extra_kwargs = {
            "card_number_encrypted": {"write_only": True}
        }

    def get_active_orders_count(self, obj):
        return obj.orders.exclude(current_status__in=['completed', 'cancelled']).count() if hasattr(obj, 'orders') else 0

