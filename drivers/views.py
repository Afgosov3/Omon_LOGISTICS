from rest_framework import viewsets, permissions
    ordering_fields = ["created_at", "full_name", "telegram_username"]
        instance.save()
        instance.deleted_at = timezone.now()
        instance.is_deleted = True
        from django.utils import timezone
    def perform_destroy(self, instance):

        serializer.save(created_by=self.request.user, joined_at=timezone.now())
        from django.utils import timezone
    def perform_create(self, serializer):
    permission_classes = [permissions.IsAuthenticated, IsDispatcherOrHigher]
    serializer_class = DriverSerializer
    queryset = Driver.objects.filter(is_deleted=False).order_by("-created_at")
    # Retrieve active drivers by default, or provide filter
class DriverViewSet(viewsets.ModelViewSet):


from .serializers import DriverSerializer
from .models import Driver
from accounts.permissions import IsDispatcherOrHigher


# Create your views here.
