from django.contrib import admin
from .models import Payout

@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ['driver', 'amount', 'status', 'created_at', 'paid_at']
    list_filter = ['status', 'created_at', 'paid_at']
    search_fields = ['driver__full_name', 'order__order_number']
    readonly_fields = ['created_at', 'updated_at']
