from rest_framework import views, permissions, response

from orders.models import Order
from drivers.models import Driver
from clients.models import Client
from vehicles.models import Vehicle


class DashboardSummaryView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        stats = {
            "total_orders": Order.objects.count(),
            "active_orders": Order.objects.exclude(current_status__in=['completed', 'cancelled']).count(),
            "total_drivers": Driver.objects.count(),
            "active_drivers": Driver.objects.filter(is_active=True).count(),
            "total_clients": Client.objects.count(),
            "total_vehicles": Vehicle.objects.count(),
        }
        return response.Response(stats)

