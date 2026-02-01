from django.db import models

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default='e-Shop')
    site_logo = models.ImageField(upload_to='site_settings/', blank=True, null=True)
    contact_email = models.EmailField(default='support@shop.com')
    contact_phone = models.CharField(max_length=20, default='+880 1711 223 344')
    address = models.TextField(default='DHAKA, BANGLADESH')
    facebook_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"

    @classmethod
    def get_settings(cls):
        settings, created = cls.objects.get_or_create(pk=1)
        return settings

class Notification(models.Model):
    from django.contrib.auth.models import User
    
    NOTIFICATION_TYPES = [
        ('admin', 'Admin Notification'),
        ('restock', 'Restock Alert'),
        ('order', 'Order Update'),
        ('warning', 'Warning'),
        ('general', 'General'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, 
                            related_name='notifications',
                            help_text="Specific user for this notification. Leave blank for admin notifications.")
    title = models.CharField(max_length=255)
    message = models.TextField()
    url = models.CharField(max_length=255, blank=True, null=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='general')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['notification_type', '-created_at']),
        ]

    def __str__(self):
        if self.user:
            return f"{self.title} (for {self.user.username})"
        return f"{self.title} (Admin)"
