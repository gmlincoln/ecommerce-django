from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'quantity', 'price')
    can_delete = False
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total', 'status', 'delivery_status', 'payment_method', 'created_at')
    list_editable = ('status', 'delivery_status')
    list_filter = ('status', 'delivery_status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__email')
    readonly_fields = ('order_number', 'transaction_id', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    ordering = ('-created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('orderitem_set__product')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('order__status',)
    search_fields = ('order__order_number', 'product__name')
    readonly_fields = ('order', 'product', 'quantity', 'price')
    ordering = ('-order__created_at',)