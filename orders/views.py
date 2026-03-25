from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

from accounts.permissions import IsDispatcherOrHigher
from drivers.models import Driver
from vehicles.models import Vehicle

from .models import Order, OrderStatus
from .serializers import (
    OrderSerializer,
    OrderStatusUpdateSerializer,
    AssignDriverSerializer,
)
from .services import OrderService


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related(
        "client",
        "assigned_driver",
        "assigned_vehicle",
        "created_by_dispatcher",
        "assigned_dispatcher"
    ).prefetch_related("points", "proofs").all().order_by("-created_at")

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsDispatcherOrHigher]
    search_fields = [
        "public_id",
        "client__full_name",
        "assigned_driver__full_name",
        "cargo_name",
    ]
    filterset_fields = [
        "current_status",
        "assigned_driver",
        "assigned_vehicle",
        "client",
    ]
    ordering_fields = ["created_at", "driver_assigned_at", "completed_at", "driver_price", "client_price"]

    def perform_create(self, serializer):
        serializer.save(created_by_dispatcher=self.request.user)

    @action(detail=True, methods=["post"], url_path="assign-driver")
    @transaction.atomic
    def assign_driver(self, request, pk=None):
        order = self.get_object()
        serializer = AssignDriverSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        driver_id = serializer.validated_data["driver_id"]
        try:
            driver = Driver.objects.get(pk=driver_id)
        except Driver.DoesNotExist:
            return Response({"error": "Driver not found"}, status=status.HTTP_404_NOT_FOUND)

        if not driver.is_active:
             return Response({"error": "Driver is inactive"}, status=status.HTTP_400_BAD_REQUEST)

        updated_order = OrderService.assign_driver(order.id, driver, user=request.user)
        return Response(OrderSerializer(updated_order).data)

    @action(detail=True, methods=["post"], url_path="update-status")
    @transaction.atomic
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        new_status = serializer.validated_data["status"]
        comment = serializer.validated_data.get("comment", "")
        proof_file = request.FILES.get("proof_file")
        proof_type = serializer.validated_data.get("proof_type")

        try:
            OrderService.update_status(
                order,
                new_status,
                user=request.user,
                comment=comment,
                proof_file=proof_file,
                proof_type=proof_type
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"status": "updated", "current_status": new_status})
