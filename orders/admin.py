from django.contrib import admin
from .models import Order, OrderProof

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['public_id', 'client', 'assigned_driver', 'current_status', 'driver_price', 'created_at']
    list_filter = ['current_status', 'created_at', 'assigned_driver']
    search_fields = ['public_id', 'client__full_name', 'cargo_name']

@admin.register(OrderProof)
class OrderProofAdmin(admin.ModelAdmin):
    list_display = ['order', 'proof_kind', 'created_at']
    list_filter = ['proof_kind', 'created_at']
    search_fields = ['order__public_id']
