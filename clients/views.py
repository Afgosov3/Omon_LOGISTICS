from rest_framework import viewsets, permissions

from accounts.permissions import IsDispatcherOrHigher
from .models import Client
from .serializers import ClientSerializer


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.filter(is_deleted=False).order_by("-created_at")
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated, IsDispatcherOrHigher]
    search_fields = ["full_name", "company_name", "phone", "email"]
    ordering_fields = ["created_at", "full_name"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        from django.utils import timezone
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()
