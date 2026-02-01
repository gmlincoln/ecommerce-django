from django import template
from django.utils import timezone
from ..models import Order

register = template.Library()

@register.simple_tag
def get_payable_count(user):
    if user.is_authenticated:
        now = timezone.now()
        from django.db.models import Q
        count = Order.objects.filter(
            user=user,
            payment_method='sslcommerz',
            payment_timeout__gt=now
        ).filter(
            Q(status='pending') | Q(status='failed')
        ).count()
        return count
    return 0

@register.simple_tag(takes_context=True)
def get_cart_count(context):
    request = context['request']
    cart = request.session.get('cart', {})
    count = sum(item['qty'] for item in cart.values()) if cart else 0
    return count
