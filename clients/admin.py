from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'email', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['full_name', 'phone', 'email']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (_('Shaxsiy ma\'lumotlar'), {
            'fields': ('full_name', 'phone', 'email')
        }),
        (_('Telegram'), {
            'fields': ('telegram_id', 'telegram_username')
        }),
        (_('Aktiv holati'), {
            'fields': ('is_active',)
        }),
        (_('Vaqtlar'), {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
