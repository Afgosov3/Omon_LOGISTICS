from rest_framework import serializers

from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "target_type",
            "target_id",
            "channel",
            "title",
            "body",
            "related_order_id",
            "is_read",
            "sent_at",
            "created_at",
        ]
        read_only_fields = ["created_at", "sent_at"]


class MarkAsReadSerializer(serializers.Serializer):
    notification_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    all = serializers.BooleanField(default=False)

