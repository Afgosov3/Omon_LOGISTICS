from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['actor_type', 'action', 'entity_type', 'actor_id', 'created_at']
    list_filter = ['action', 'created_at', 'entity_type', 'actor_type']
    search_fields = ['actor_id', 'entity_id', 'action']
