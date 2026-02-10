from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'email', 'status', 'total', 'created_at']
    list_filter = ['status', 'created_at']
    list_editable = ['status']
    search_fields = ['order_number', 'email', 'shipping_name']
    readonly_fields = ['order_number', 'stripe_checkout_session_id', 'stripe_payment_intent_id']
    inlines = [OrderItemInline]
