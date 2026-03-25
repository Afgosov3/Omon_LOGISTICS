from rest_framework import serializers

from .models import Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source="driver.full_name", read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "driver",
            "driver_name",
            "type",
            "brand",
            "model",
            "plate_number",
            "capacity_kg",
            "volume_m3",
            "is_active",
            "created_at",
            "updated_at",
        ]
