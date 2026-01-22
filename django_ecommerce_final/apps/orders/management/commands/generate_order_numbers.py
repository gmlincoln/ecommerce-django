from django.core.management.base import BaseCommand
from apps.orders.models import Order


class Command(BaseCommand):
    help = 'Generate order numbers for orders that have None order_number'

    def handle(self, *args, **options):
        # Find orders with None order numbers
        none_orders = Order.objects.filter(order_number__isnull=True)
        updated_count = 0

        for order in none_orders:
            # Save will trigger the order number generation
            order.save()
            self.stdout.write(
                self.style.SUCCESS(f'Generated order number {order.order_number} for Order ID {order.id}')
            )
            updated_count += 1

        if updated_count == 0:
            self.stdout.write('No orders with None order_number found.')
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully generated order numbers for {updated_count} order(s).')
            )