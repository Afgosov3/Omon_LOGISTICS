from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Notification, TargetType
from .serializers import NotificationSerializer, MarkAsReadSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all().order_by("-created_at")
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["is_read", "channel", "target_type"]

    def get_queryset(self):
        # Filter notifications relevant to current user?
        # For now, if admin/dispatcher see all or logic?
        # If user is admin/dispatcher, maybe filter by target_type=USER or ALL?
        # This needs logic adjustments based on requirements.
        # Assuming admin sees all for now or notifications targeted to them.
        return super().get_queryset()

    @action(detail=False, methods=["post"], url_path="mark-read")
    def mark_as_read(self, request):
        serializer = MarkAsReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data.get("all"):
            # Mark all unread for this user context?
            self.get_queryset().filter(is_read=False).update(is_read=True)
            return Response({"status": "All marked as read"})

        ids = serializer.validated_data.get("notification_ids", [])
        if ids:
            self.get_queryset().filter(id__in=ids).update(is_read=True)
            return Response({"status": "Marked as read"})

        return Response({"status": "No action"})
