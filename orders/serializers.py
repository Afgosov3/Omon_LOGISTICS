from rest_framework import serializers

from .models import Order, OrderProof, OrderStatusHistory, OrderPoint, OrderStatus, ProofKind

class OrderPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderPoint
        fields = [
            "id",
            "point_type",
            "sequence",
            "address",
            "latitude",
            "longitude",
            "contact_person",
            "contact_phone",
        ]


class OrderProofSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProof
        fields = ["id", "file", "file_type", "proof_kind", "comment", "created_at"]
        read_only_fields = ["created_at"]


class OrderSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.full_name", read_only=True)
    driver_name = serializers.CharField(
        source="assigned_driver.full_name", read_only=True
    )
    vehicle_plate = serializers.CharField(
        source="assigned_vehicle.plate_number", read_only=True
    )
    created_by_name = serializers.CharField(
        source="created_by_dispatcher.get_full_name", read_only=True
    )
    points = OrderPointSerializer(many=True, required=False)
    proofs = OrderProofSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "public_id",
            "client",
            "client_name",
            "assigned_driver",
            "driver_name",
            "assigned_vehicle",
            "vehicle_plate",
            "created_by_dispatcher",
            "created_by_name",
            "assigned_dispatcher",
            "cargo_name",
            "cargo_description",
            "cargo_weight_kg",
            "cargo_volume_m3",
            "cargo_category",
            "client_price",
            "driver_price",
            "current_status",
            "internal_comment",
            "completed_at",
            "driver_assigned_at",
            "estimated_distance_km",
            "estimated_duration_minutes",
            "created_at",
            "updated_at",
            "points",
            "proofs",
        ]
        read_only_fields = [
            "id",
            "public_id",
            "created_by_dispatcher",
            "completed_at",
            "driver_assigned_at",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        points_data = validated_data.pop("points", [])
        order = Order.objects.create(**validated_data)

        for point in points_data:
            OrderPoint.objects.create(order=order, **point)

        return order


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=OrderStatus.choices)
    proof_file = serializers.FileField(required=False)
    proof_type = serializers.ChoiceField(choices=ProofKind.choices, required=False)
    comment = serializers.CharField(required=False, allow_blank=True)


class AssignDriverSerializer(serializers.Serializer):
    driver_id = serializers.IntegerField()


class AssignVehicleSerializer(serializers.Serializer):
    vehicle_id = serializers.IntegerField()

