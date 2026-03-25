from django.contrib import admin
from .models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['plate_number', 'type', 'driver', 'is_active', 'created_at']
    list_filter = ['type', 'is_active', 'created_at']
    search_fields = ['plate_number', 'driver__full_name', 'model']
