from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    icon = models.CharField(max_length=50, default="fas fa-tag", help_text="FontAwesome icon class")
    
    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=10)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        return self.stock > 0

    def save(self, *args, **kwargs):
        # Prevent negative stock
        if self.stock < 0:
            self.stock = 0
        
        # Check stock changes for existing products
        if self.pk:
            try:
                old_product = Product.objects.get(pk=self.pk)
                
                # If stock was positive and now is 0 or below, create admin notification
                if old_product.stock > 0 and self.stock <= 0:
                    from apps.custom_admin.models import Notification
                    Notification.objects.create(
                        title=f"Product Out of Stock",
                        message=f"'{self.name}' is now out of stock.",
                        notification_type='warning'
                    )
                
                # If stock was 0 and now is positive, notify subscribed users
                if old_product.stock <= 0 and self.stock > 0:
                    self._send_restock_notifications()
                    
            except Product.DoesNotExist:
                pass
        
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def _send_restock_notifications(self):
        """Send notifications to users who subscribed for restock alerts"""
        from apps.custom_admin.models import Notification
        from django.utils import timezone
        
        # Get all users subscribed to this product's restock notifications
        subscriptions = self.restock_subscribers.filter(notified=False)
        
        for subscription in subscriptions:
            # Create user-specific notification
            Notification.objects.create(
                user=subscription.user,
                title=f"Product Back in Stock!",
                message=f"'{self.name}' is now available. Order now before it runs out!",
                notification_type='restock',
                url=self.get_absolute_url()
            )
            
            # Mark subscription as notified
            subscription.notified = True
            subscription.notified_at = timezone.now()
            subscription.save()
        
    def get_absolute_url(self):
        return reverse('product_detail', args=[self.slug])

    def get_active_campaign(self):
        """Returns the first active campaign this product belongs to."""
        from django.utils import timezone
        now = timezone.now()
        # Filter campaigns that are active and currently within their time range
        return self.campaigns.filter(
            is_active=True,
            start_time__lte=now,
            end_time__gte=now
        ).first()

    def get_display_price(self):
        """Calculates and returns the discounted price if an active campaign exists."""
        campaign = self.get_active_campaign()
        if campaign and campaign.discount_percentage > 0:
            from decimal import Decimal
            discount = (self.price * Decimal(campaign.discount_percentage)) / Decimal(100)
            return (self.price - discount).quantize(Decimal('0.01'))
        return self.price

class Campaign(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='campaigns/', blank=True, null=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    discount_percentage = models.PositiveIntegerField(default=0)
    
    # Products associated with this campaign
    products = models.ManyToManyField(Product, related_name='campaigns')

    def __str__(self):
        return self.title

    @property
    def is_running(self):
        from django.utils import timezone
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    @property
    def is_upcoming(self):
        from django.utils import timezone
        return timezone.now() < self.start_time

class Wishlist(models.Model):
    """Model to store user wishlists"""
    from django.contrib.auth.models import User
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']
        verbose_name = 'Wishlist Item'
        verbose_name_plural = 'Wishlist Items'
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

class RestockNotification(models.Model):
    """Model to track restock notification requests"""
    from django.contrib.auth.models import User
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='restock_notifications')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='restock_subscribers')
    notified = models.BooleanField(default=False, help_text="Whether the user has been notified")
    created_at = models.DateTimeField(auto_now_add=True)
    notified_at = models.DateTimeField(null=True, blank=True, help_text="When the notification was sent")
    
    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']
        verbose_name = 'Restock Notification'
        verbose_name_plural = 'Restock Notifications'
    
    def __str__(self):
        status = "Notified" if self.notified else "Pending"
        return f"{self.user.username} - {self.product.name} ({status})"
