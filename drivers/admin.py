from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Driver

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'is_active', 'is_online', 'created_at']
    list_filter = ['is_active', 'is_online', 'created_at']
    search_fields = ['full_name', 'phone', 'telegram_username']
    readonly_fields = ['created_at', 'updated_at', 'last_location_update']

    fieldsets = (
        (_('Shaxsiy ma\'lumotlar'), {
            'fields': ('full_name', 'phone', 'email')
        }),
        (_('Telegram'), {
            'fields': ('telegram_id', 'telegram_username')
        }),
        (_('Lokatsiya'), {
            'fields': ('current_lat', 'current_lng', 'last_location_update'),
            'classes': ('collapse',)
        }),
        (_('Hisob'), {
            'fields': ('account_number', 'card_last4')
        }),
        (_('Aktiv holati'), {
            'fields': ('is_active', 'is_online')
        }),
        (_('Vaqtlar'), {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
