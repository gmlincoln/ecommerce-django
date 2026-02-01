from django.contrib import admin
from .models import SiteSettings, Notification

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'contact_email', 'contact_phone']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['title', 'message']
