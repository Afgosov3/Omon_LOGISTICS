from rest_framework import viewsets, permissions

from accounts.permissions import IsDispatcherOrHigher
from .models import Driver
from .serializers import DriverSerializer


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.filter(is_deleted=False).order_by("-created_at")
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAuthenticated, IsDispatcherOrHigher]
    search_fields = ["full_name", "phone", "telegram_username"]
    ordering_fields = ["created_at", "full_name", "telegram_username"]

    def perform_create(self, serializer):
        from django.utils import timezone
        serializer.save(created_by=self.request.user, joined_at=timezone.now())

    def perform_destroy(self, instance):
        from django.utils import timezone
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()
from accounts.permissions import IsDispatcherOrHigher


# Create your views here.
