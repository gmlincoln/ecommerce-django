from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from apps.orders.models import Order, OrderItem
from apps.store.models import Product
from django.contrib.auth.models import User
import csv
from django.http import HttpResponse


def get_dashboard_stats():
    """
    Calculate dashboard statistics
    """
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Sales statistics
    stats = {
        'total_revenue': Order.objects.filter(status='completed').aggregate(
            total=Sum('total'))['total'] or 0,
        'today_revenue': Order.objects.filter(
            status='completed', 
            created_at__date=today
        ).aggregate(total=Sum('total'))['total'] or 0,
        'week_revenue': Order.objects.filter(
            status='completed', 
            created_at__date__gte=week_ago
        ).aggregate(total=Sum('total'))['total'] or 0,
        'month_revenue': Order.objects.filter(
            status='completed', 
            created_at__date__gte=month_ago
        ).aggregate(total=Sum('total'))['total'] or 0,
        
        # Order counts
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'completed_orders': Order.objects.filter(status='completed').count(),
        'today_orders': Order.objects.filter(created_at__date=today).count(),
        
        # Product statistics
        'total_products': Product.objects.count(),
        'low_stock_products': Product.objects.filter(stock__lt=10).count(),
        'out_of_stock_products': Product.objects.filter(stock=0).count(),
        
        # User statistics
        'total_users': User.objects.count(),
        'new_users_today': User.objects.filter(date_joined__date=today).count(),
    }
    
    return stats


def get_recent_orders(limit=10):
    """
    Get recent orders with related data
    """
    return Order.objects.select_related('user').prefetch_related(
        'orderitem_set__product'
    ).order_by('-created_at')[:limit]


def get_top_selling_products(limit=10):
    """
    Get top selling products based on order items
    """
    return Product.objects.annotate(
        total_sold=Sum('orderitem__quantity')
    ).filter(total_sold__isnull=False).order_by('-total_sold')[:limit]


def get_low_stock_products(threshold=10):
    """
    Get products with low stock
    """
    return Product.objects.filter(stock__lt=threshold, stock__gt=0).order_by('stock')


def get_sales_chart_data(days=30):
    """
    Get sales data for chart (last N days)
    """
    today = timezone.now().date()
    start_date = today - timedelta(days=days)
    
    # Get daily sales
    daily_sales = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        revenue = Order.objects.filter(
            status='completed',
            created_at__date=date
        ).aggregate(total=Sum('total'))['total'] or 0
        
        daily_sales.append({
            'date': date.strftime('%Y-%m-%d'),
            'revenue': float(revenue)
        })
    
    return daily_sales


def export_orders_csv(queryset):
    """
    Export orders to CSV
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Order Number', 'User', 'Total', 'Status', 
        'Delivery Status', 'Payment Method', 'Created At'
    ])
    
    for order in queryset:
        writer.writerow([
            order.order_number,
            order.user.username,
            order.total,
            order.status,
            order.delivery_status,
            order.payment_method,
            order.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response


def export_products_csv(queryset):
    """
    Export products to CSV
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Name', 'Category', 'Price', 'Stock', 
        'Is Featured', 'Created At'
    ])
    
    for product in queryset:
        writer.writerow([
            product.name,
            product.category.name if product.category else '',
            product.price,
            product.stock,
            product.is_featured,
            product.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response
