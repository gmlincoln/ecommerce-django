from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.orders.models import Order


class Command(BaseCommand):
    help = 'Cancel orders that have expired payment timeout'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Find pending SSL Commerce orders that have expired
        expired_orders = Order.objects.filter(
            status='pending',
            payment_method='sslcommerz',
            payment_timeout__lt=now
        )
        
        cancelled_count = 0
        for order in expired_orders:
            order.status = 'cancelled'
            order.save()
            cancelled_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Cancelled order #{order.order_number} (expired at {order.payment_timeout})')
            )
        
        if cancelled_count == 0:
            self.stdout.write('No expired orders found.')
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully cancelled {cancelled_count} expired order(s).')
            )