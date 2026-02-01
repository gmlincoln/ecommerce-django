from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from .decorators import admin_required
from .utils import (
    get_dashboard_stats, get_recent_orders, get_top_selling_products,
    get_low_stock_products, get_sales_chart_data, export_orders_csv,
    export_products_csv
)
from .forms import ProductForm, CategoryForm, CampaignForm, OrderStatusForm, SiteSettingsForm
from .models import SiteSettings, Notification
from apps.store.models import Product, Category, Campaign
from apps.orders.models import Order, OrderItem
from django.contrib.auth.models import User
from apps.accounts.models import Profile


@admin_required
def dashboard(request):
    """
    Admin dashboard with statistics and charts
    """
    stats = get_dashboard_stats()
    recent_orders = get_recent_orders(limit=10)
    top_products = get_top_selling_products(limit=5)
    low_stock = get_low_stock_products(threshold=10)
    sales_data = get_sales_chart_data(days=30)
    
    # Get out-of-stock products
    out_of_stock_products = Product.objects.filter(stock=0).order_by('name')
    
    categories = Category.objects.annotate(product_count=Count('products')).all()
    
    context = {
        'stats': stats,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'low_stock': low_stock,
        'sales_data': sales_data,
        'categories': categories,
        'out_of_stock_products': out_of_stock_products,
        'out_of_stock_count': out_of_stock_products.count(),
    }
    return render(request, 'custom_admin/dashboard.html', context)


# ============= PRODUCT MANAGEMENT =============

@admin_required
def product_list(request):
    """
    List all products with search and filter
    """
    products = Product.objects.select_related('category').all()
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Filter by category
    category_id = request.GET.get('category', '')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Filter by stock status
    stock_filter = request.GET.get('stock', '')
    if stock_filter == 'low':
        products = products.filter(stock__lt=10, stock__gt=0)
    elif stock_filter == 'out':
        products = products.filter(stock=0)
    
    # Pagination
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = list(Category.objects.all())
    for cat in categories:
        cat.is_selected = str(cat.id) == category_id
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
        'stock_filter': stock_filter,
        'is_low_stock': stock_filter == 'low',
        'is_out_stock': stock_filter == 'out',
    }
    return render(request, 'custom_admin/products/product_list.html', context)


@admin_required
def product_create(request):
    """
    Create new product
    """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully!')
            return redirect('custom_admin:product_list')
    else:
        form = ProductForm()
    
    context = {'form': form, 'action': 'Create'}
    return render(request, 'custom_admin/products/product_form.html', context)


@admin_required
def product_edit(request, pk):
    """
    Edit existing product
    """
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('custom_admin:product_list')
    else:
        form = ProductForm(instance=product)
    
    context = {'form': form, 'product': product, 'action': 'Edit'}
    return render(request, 'custom_admin/products/product_form.html', context)


@admin_required
def product_delete(request, pk):
    """
    Delete product
    """
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('custom_admin:product_list')
    
    context = {'product': product}
    return render(request, 'custom_admin/products/product_confirm_delete.html', context)


@admin_required
def product_export(request):
    """
    Export products to CSV
    """
    products = Product.objects.select_related('category').all()
    return export_products_csv(products)


@admin_required
def product_bulk_delete(request):
    """
    Bulk delete products
    """
    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids')
        if product_ids:
            Product.objects.filter(id__in=product_ids).delete()
            messages.success(request, f'Successfully deleted {len(product_ids)} products.')
        else:
            messages.warning(request, 'No products selected.')
    return redirect('custom_admin:product_list')


# ============= CATEGORY MANAGEMENT =============

@admin_required
def category_list(request):
    """
    List all categories
    """
    categories = Category.objects.annotate(
        product_count=Count('products')
    ).all()
    
    context = {'categories': categories}
    return render(request, 'custom_admin/products/category_list.html', context)


@admin_required
def category_create(request):
    """
    Create new category
    """
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('custom_admin:category_list')
    else:
        form = CategoryForm()
    
    context = {'form': form, 'action': 'Create'}
    return render(request, 'custom_admin/products/category_form.html', context)


@admin_required
def category_edit(request, pk):
    """
    Edit existing category
    """
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('custom_admin:category_list')
    else:
        form = CategoryForm(instance=category)
    
    context = {'form': form, 'category': category, 'action': 'Edit'}
    return render(request, 'custom_admin/products/category_form.html', context)


@admin_required
def category_delete(request, pk):
    """
    Delete category
    """
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('custom_admin:category_list')
    
    context = {'category': category}
    return render(request, 'custom_admin/products/category_confirm_delete.html', context)


# ============= CAMPAIGN MANAGEMENT =============

@admin_required
def campaign_list(request):
    """
    List all campaigns
    """
    campaigns = Campaign.objects.prefetch_related('products').all()
    
    context = {'campaigns': campaigns}
    return render(request, 'custom_admin/products/campaign_list.html', context)


@admin_required
def campaign_create(request):
    """
    Create new campaign
    """
    if request.method == 'POST':
        form = CampaignForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campaign created successfully!')
            return redirect('custom_admin:campaign_list')
    else:
        form = CampaignForm()
    
    context = {'form': form, 'action': 'Create'}
    return render(request, 'custom_admin/products/campaign_form.html', context)


@admin_required
def campaign_edit(request, pk):
    """
    Edit existing campaign
    """
    campaign = get_object_or_404(Campaign, pk=pk)
    
    if request.method == 'POST':
        form = CampaignForm(request.POST, request.FILES, instance=campaign)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campaign updated successfully!')
            return redirect('custom_admin:campaign_list')
    else:
        form = CampaignForm(instance=campaign)
    
    context = {'form': form, 'campaign': campaign, 'action': 'Edit'}
    return render(request, 'custom_admin/products/campaign_form.html', context)


@admin_required
def campaign_delete(request, pk):
    """
    Delete campaign
    """
    campaign = get_object_or_404(Campaign, pk=pk)
    if request.method == 'POST':
        campaign.delete()
        messages.success(request, 'Campaign deleted successfully!')
        return redirect('custom_admin:campaign_list')
    
    context = {'campaign': campaign}
    return render(request, 'custom_admin/products/campaign_confirm_delete.html', context)


# ============= ORDER MANAGEMENT =============

@admin_required
def order_list(request):
    """
    List all orders with filters
    """
    orders = Order.objects.select_related('user').prefetch_related('orderitem_set__product').all()
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Filter by delivery status
    delivery_filter = request.GET.get('delivery', '')
    if delivery_filter:
        orders = orders.filter(delivery_status=delivery_filter)
    
    # Pagination
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    from apps.orders.models import ORDER_STATUS_CHOICES, DELIVERY_STATUS_CHOICES
    
    # Process choices to include is_selected
    status_choices = []
    for val, lbl in ORDER_STATUS_CHOICES:
        status_choices.append({
            'value': val,
            'label': lbl,
            'is_selected': val == status_filter
        })
        
    delivery_choices = []
    for val, lbl in DELIVERY_STATUS_CHOICES:
        delivery_choices.append({
            'value': val,
            'label': lbl,
            'is_selected': val == delivery_filter
        })

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'delivery_filter': delivery_filter,
        'status_choices': status_choices,
        'delivery_choices': delivery_choices,
    }
    return render(request, 'custom_admin/orders/order_list.html', context)


@admin_required
def order_detail(request, pk):
    """
    View order details and update status
    """
    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related('orderitem_set__product'),
        pk=pk
    )
    
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Order status updated successfully!')
            return redirect('custom_admin:order_detail', pk=pk)
    else:
        form = OrderStatusForm(instance=order)
    
    context = {
        'order': order,
        'form': form,
    }
    return render(request, 'custom_admin/orders/order_detail.html', context)

@admin_required
def order_invoice(request, pk):
    """
    Generate professional printable invoice
    """
    order = get_object_or_404(Order, pk=pk)
    settings = SiteSettings.get_settings()
    # Ensure site_name exists for the template
    if not settings.site_name:
        settings.site_name = "e-Shop"
    
    return render(request, 'custom_admin/orders/order_invoice.html', {
        'order': order,
        'settings': settings
    })


@admin_required
def order_export(request):
    """
    Export orders to CSV
    """
    orders = Order.objects.select_related('user').all()
    return export_orders_csv(orders)


@admin_required
def order_bulk_status(request):
    """
    Bulk update order status
    """
    if request.method == 'POST':
        order_ids = request.POST.getlist('order_ids')
        new_status = request.POST.get('new_status')
        if order_ids and new_status:
            Order.objects.filter(id__in=order_ids).update(status=new_status)
            messages.success(request, f'Successfully updated {len(order_ids)} orders to {new_status}.')
        else:
            messages.warning(request, 'No orders or status selected.')
    return redirect('custom_admin:order_list')


# ============= USER MANAGEMENT =============

@admin_required
def user_list(request):
    """
    List all users
    """
    users = User.objects.select_related('profile').all()
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'custom_admin/users/user_list.html', context)


@admin_required
def user_detail(request, pk):
    """
    View user details and order history
    """
    user = get_object_or_404(User.objects.select_related('profile'), pk=pk)
    orders = Order.objects.filter(user=user).order_by('-created_at')
    
    # Pagination for orders
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'user_obj': user,
        'page_obj': page_obj,
    }
    return render(request, 'custom_admin/users/user_detail.html', context)


# ============= ANALYTICS =============

@admin_required
def analytics(request):
    """
    Analytics and reports page
    """
    stats = get_dashboard_stats()
    sales_data = get_sales_chart_data(days=30)
    top_products = get_top_selling_products(limit=10)
    
    context = {
        'stats': stats,
        'sales_data': sales_data,
        'top_products': top_products,
    }
    return render(request, 'custom_admin/analytics/reports.html', context)


# ============= API ENDPOINTS =============

@admin_required
def api_sales_data(request):
    """
    API endpoint for sales chart data
    """
    days = int(request.GET.get('days', 30))
    data = get_sales_chart_data(days=days)
    return JsonResponse({'data': data})


@admin_required
def site_settings(request):
    """
    Manage site-wide settings
    """
    settings = SiteSettings.get_settings()
    if request.method == 'POST':
        form = SiteSettingsForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Site settings updated successfully!')
            return redirect('custom_admin:site_settings')
    else:
        form = SiteSettingsForm(instance=settings)
    
    return render(request, 'custom_admin/settings/site_settings.html', {
        'form': form,
        'settings': settings
    })
@admin_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    notification.is_read = True
    notification.save()
    if notification.url:
        return redirect(notification.url)
    return redirect('custom_admin:dashboard')

@admin_required
def mark_all_notifications_read(request):
    Notification.objects.filter(is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect(request.META.get('HTTP_REFERER', 'custom_admin:dashboard'))
