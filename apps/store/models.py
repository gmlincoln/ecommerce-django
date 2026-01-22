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

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def get_absolute_url(self):
        return reverse('product_detail', args=[self.slug])

class Campaign(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='campaigns/', blank=True, null=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    discount_percent = models.IntegerField(default=10, help_text="Discount percentage for campaign products (0-100)")
    
    # Products associated with this campaign
    products = models.ManyToManyField(Product, related_name='campaigns')

    def __str__(self):
        return self.title

    @property
    def is_running(self):
        from django.utils import timezone
        now = timezone.now()
        
        # If no start_time, consider it as started
        if self.start_time is None:
            start_check = True
        else:
            start_check = now >= self.start_time
        
        # If no end_time, consider it as never ending (runs forever)
        if self.end_time is None:
            end_check = True
        else:
            end_check = now <= self.end_time
        
        return start_check and end_check

    @property
    def is_upcoming(self):
        from django.utils import timezone
        if self.start_time is None:
            return False
        return timezone.now() < self.start_time
