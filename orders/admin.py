from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Order, OrderProof

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['public_id', 'client', 'assigned_driver', 'current_status', 'driver_price', 'created_at']
    list_filter = ['current_status', 'created_at', 'assigned_driver']
    search_fields = ['public_id', 'client__full_name', 'cargo_name']
    readonly_fields = ['public_id', 'created_at', 'updated_at']

    fieldsets = (
        (_('Asosiy ma\'lumotlar'), {
            'fields': ('public_id', 'client', 'cargo_name', 'cargo_description')
        }),
        (_('Joylar'), {
            'fields': ('assigned_driver', 'assigned_vehicle', 'assigned_dispatcher')
        }),
        (_('Narxlar'), {
            'fields': ('client_price', 'driver_price')
        }),
        (_('Statuslar'), {
            'fields': ('current_status', 'assigned_at', 'deleted_at')
        }),
        (_('Vaqtlar'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(OrderProof)
class OrderProofAdmin(admin.ModelAdmin):
    list_display = ['order', 'proof_kind', 'created_at']
    list_filter = ['proof_kind', 'created_at']
    search_fields = ['order__public_id']
    readonly_fields = ['created_at']
