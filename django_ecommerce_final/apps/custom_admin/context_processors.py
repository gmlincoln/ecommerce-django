from .models import Notification, SiteSettings

def admin_notifications(request):
    context = {}
    if request.user.is_authenticated and request.user.is_staff:
        notifications = Notification.objects.filter(is_read=False)[:5]
        unread_count = Notification.objects.filter(is_read=False).count()
        context = {
            'admin_notifications': notifications,
            'unread_notifications_count': unread_count,
            'site_settings': SiteSettings.get_settings()
        }
    return context
