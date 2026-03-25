from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'target_type', 'channel', 'is_read', 'created_at']
    list_filter = ['channel', 'is_read', 'created_at', 'target_type']
    search_fields = ['title', 'body']
