from rest_framework import serializers

from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    orders_count = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            "id",
            "full_name",
            "company_name",
            "phone",
            "email",
            "address",
            "telegram_id",
            "telegram_username",
            "language",
            "notes",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
            "orders_count",
            "total_spent",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at"]

    def get_orders_count(self, obj):
        return obj.orders.count()

    def get_total_spent(self, obj):
        # Calculate sum of completed orders
        from django.db.models import Sum
        return obj.orders.filter(current_status="completed").aggregate(t=Sum('client_price'))['t'] or 0

