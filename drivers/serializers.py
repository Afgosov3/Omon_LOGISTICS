from rest_framework import serializers
from .models import Driver

class DriverSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    active_orders_count = serializers.SerializerMethodField()
    vehicle_info = serializers.SerializerMethodField()

    class Meta:
        model = Driver
        fields = [
            "id",
            "full_name",
            "phone",
            "telegram_id",
            "telegram_username",
            "card_holder_name",
            "card_number_encrypted", # Mask in real serialized representation if needed
            "card_mask",
            "is_active",
            "is_online",
            "joined_at",
            "notes",
            "created_by",
            "created_by_name",
            "active_orders_count",
            "vehicle_info",
            "card_last4",
            "current_lat",
            "current_long",
            "last_location_at",
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
            "vehicle_info",
            "card_mask",
            "card_last4"
        ]
        extra_kwargs = {
            "card_number_encrypted": {"write_only": True}
        }

    def get_active_orders_count(self, obj):
        # We can optimize this later
        return obj.orders.exclude(current_status__in=['completed', 'cancelled']).count()

    def get_vehicle_info(self, obj):
        vehicle = obj.vehicles.filter(is_active=True).first()
        if vehicle:
            return f"{vehicle.plate_number} ({vehicle.model})"
        return None

    def create(self, validated_data):
        # Handle card encryption here if needed or in perform_create
        # For now, simple create
        return super().create(validated_data)

