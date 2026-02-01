
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.store.models import Product

ORDER_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
    ('cancelled', 'Cancelled'),
]

PAYMENT_METHOD_CHOICES = [
    ('sslcommerz', 'SSLCommerz'),
    ('cod', 'Cash on Delivery'),
]

DELIVERY_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('shipped', 'Shipped'),
    ('out_for_delivery', 'Out for Delivery'),
    ('delivered', 'Delivered'),
]

class Order(models.Model):
 user=models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
 order_number=models.CharField(max_length=20, unique=True, blank=True, null=True)
 total=models.DecimalField(max_digits=10, decimal_places=2)
 shipping_charge=models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
 status=models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
 delivery_status=models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, default='pending')
 payment_method=models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='sslcommerz')
 
 # Address fields
 full_name=models.CharField(max_length=100, blank=True, null=True)
 phone=models.CharField(max_length=20, blank=True, null=True)
 email=models.EmailField(blank=True, null=True)
 address_line_1=models.CharField(max_length=255, blank=True, null=True)
 address_line_2=models.CharField(max_length=255, blank=True, null=True)
 city=models.CharField(max_length=100, blank=True, null=True)
 state=models.CharField(max_length=100, blank=True, null=True)
 postal_code=models.CharField(max_length=20, blank=True, null=True)
 country=models.CharField(max_length=100, default='Bangladesh', blank=True, null=True)
 
 transaction_id=models.CharField(max_length=255, blank=True, null=True, unique=True)
 payment_timeout=models.DateTimeField(blank=True, null=True)
 created_at=models.DateTimeField(auto_now_add=True)
 updated_at=models.DateTimeField(auto_now=True)

 def save(self, *args, **kwargs):
  if not self.order_number:
   self.order_number = self.generate_order_number()
  
  # Set payment timeout for SSL Commerce orders
  if self.payment_method == 'sslcommerz' and not self.payment_timeout:
   self.payment_timeout = timezone.now() + timezone.timedelta(minutes=30)
   
  super().save(*args, **kwargs)
 
 def check_and_cancel_if_expired(self):
  """Check if SSLCommerz order is expired and cancel if so"""
  if ((self.status == 'pending' or self.status == 'failed') and 
   self.payment_method == 'sslcommerz' and 
   self.payment_timeout and 
   self.payment_timeout < timezone.now()):
   self.status = 'cancelled'
   self.delivery_status = 'cancelled'
   self.save()
   return True
  return False

 def get_subtotal(self):
  """Calculate subtotal (total - shipping)"""
  return self.total - self.shipping_charge

 @property
 def total_items(self):
  return self.orderitem_set.count()

 def generate_order_number(self):
  """Generate order number in format: YYYYMMDDXX (date + 2-digit sequential number)"""
  today = timezone.localtime(timezone.now()).date()
  date_str = today.strftime('%Y%m%d')
  
  # Get the last order number for today
  last_order = Order.objects.filter(
   order_number__startswith=date_str
  ).order_by('-order_number').first()
  
  if last_order:
   # Extract the sequential number and increment
   last_num = int(last_order.order_number[-2:])
   new_num = last_num + 1
  else:
   new_num = 1
  
  return f"{date_str}{new_num:02d}"

 class Meta:
  ordering = ['-created_at']

 def __str__(self):
  return f"Order #{self.order_number} - {self.user.username}"

class OrderItem(models.Model):
 order=models.ForeignKey(Order, on_delete=models.CASCADE)
 product=models.ForeignKey(Product, on_delete=models.CASCADE)
 quantity=models.IntegerField()
 price=models.DecimalField(max_digits=10, decimal_places=2)

 def get_total_price(self):
  return self.quantity * self.price

 def __str__(self):
  return f"{self.product.name} x {self.quantity}"
