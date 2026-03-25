from rest_framework import viewsets, permissions

from accounts.permissions import IsDispatcherOrHigher
from .models import Vehicle
from .serializers import VehicleSerializer


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.filter(is_active=True).order_by("created_at")
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated, IsDispatcherOrHigher]
    search_fields = ["plate_number", "driver__full_name", "type"]
    filterset_fields = ["driver", "type", "is_active"]
