from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from accounts.permissions import IsFinanceOnly
from .models import Payout, PayoutStatus
from .serializers import PayoutSerializer


class PayoutViewSet(viewsets.ModelViewSet):
    queryset = Payout.objects.all().order_by("-created_at")
    serializer_class = PayoutSerializer
    permission_classes = [permissions.IsAuthenticated, IsFinanceOnly]
    search_fields = ["driver__full_name", "order__public_id"]
    filterset_fields = ["status", "payment_method", "driver"]

    @action(detail=True, methods=["post"], url_path="pay")
    def mark_as_paid(self, request, pk=None):
        payout = self.get_object()
        if payout.status == PayoutStatus.PAID:
            return Response({"error": "Already paid"}, status=status.HTTP_400_BAD_REQUEST)

        payout.status = PayoutStatus.PAID
        payout.paid_by_user = request.user
        payout.paid_at = timezone.now()

        # Optional: receipt
        if "receipt_file" in request.FILES:
            payout.receipt_file = request.FILES["receipt_file"]

        payout.comment = request.data.get("comment", payout.comment)
        payout.save()

        # Update order logic if necessary (e.g. order complete if payout is last step?)
        # For now just update Payout

        return Response(PayoutSerializer(payout).data)

