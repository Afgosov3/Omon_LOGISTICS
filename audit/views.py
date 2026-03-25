from rest_framework import viewsets, permissions

from accounts.permissions import IsAdminOnly
from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all().order_by("-created_at")
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOnly]
    filterset_fields = ["action", "entity_type", "actor_type"]
    search_fields = ["before_json", "after_json", "user_agent"]
