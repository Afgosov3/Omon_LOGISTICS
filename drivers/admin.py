from django.contrib import admin
from .models import Driver

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'is_active', 'is_online', 'created_at']
    list_filter = ['is_active', 'is_online', 'created_at']
    search_fields = ['full_name', 'phone', 'telegram_username']
    readonly_fields = ['created_at', 'updated_at', 'last_location_update']
