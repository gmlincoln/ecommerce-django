from django import template

register = template.Library()

@register.filter
def discount_price(price, discount_percent=10):
    """Calculate discounted price. Default 10% discount."""
    try:
        price = float(price)
        discount = price * (discount_percent / 100)
        return round(price - discount, 2)
    except (ValueError, TypeError):
        return price
