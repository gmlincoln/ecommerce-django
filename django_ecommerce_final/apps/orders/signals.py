from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, OrderItem
from apps.custom_admin.models import Notification
from django.urls import reverse

@receiver(post_save, sender=Order)
def create_order_notification(sender, instance, created, **kwargs):
    if created:
        customer_name = instance.full_name or instance.user.username
        Notification.objects.create(
            title=f"New Order from {customer_name}",
            message=f"Order #{instance.order_number} for ৳{instance.total} has been placed.",
            url=reverse('custom_admin:order_detail', kwargs={'pk': instance.pk})
        )

@receiver(post_save, sender=OrderItem)
def handle_stock_on_order_item(sender, instance, created, **kwargs):
    if created:
        # Decrease stock for the product
        product = instance.product
        product.stock -= instance.quantity
        product.save()
        
        # If stock is less than 5, create a low stock notification
        if product.stock < 5:
            Notification.objects.create(
                title=f"Low Stock Alert: {product.name}",
                message=f"Only {product.stock} units left in stock! Please restock soon.",
                url=reverse('custom_admin:product_list')
            )
