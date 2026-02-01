
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from .models import Product, Category, Campaign
from .cart import Cart
from django.utils import timezone

def home(request):
    query = request.GET.get('query')
    category_slug = request.GET.get('category')
    sort_by = request.GET.get('sort', 'latest')
    
    products = Product.objects.all()
    categories = Category.objects.all()
    
    # Active Campaign with products
    campaign = Campaign.objects.filter(is_active=True, end_time__gt=timezone.now()).first()
    
    if query:
        products = products.filter(name__icontains=query)
    
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    # Apply sorting
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    else:  # latest
        products = products.order_by('-created_at')
        
    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'campaign': campaign,
        'current_category': category_slug,
        'current_sort': sort_by
    }
    return render(request, 'store/home.html', context)

def product_detail(request, slug=None, id=None):
    if slug:
        product = get_object_or_404(Product, slug=slug)
    else:
        product = get_object_or_404(Product, id=id)
    
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    
    # Check if user is authenticated and has this product in wishlist
    in_wishlist = False
    restock_subscribed = False
    if request.user.is_authenticated:
        from .models import Wishlist, RestockNotification
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
        restock_subscribed = RestockNotification.objects.filter(
            user=request.user, 
            product=product,
            notified=False
        ).exists()
    
    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'in_wishlist': in_wishlist,
        'restock_subscribed': restock_subscribed
    })

def campaign_detail(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    products = campaign.products.all()
    return render(request, 'store/campaign_detail.html', {
        'campaign': campaign,
        'products': products
    })

@login_required
def add_to_cart(request,id):
    from django.contrib import messages
    p=get_object_or_404(Product,id=id)
    
    # Check if product is in stock
    if not p.is_in_stock:
        messages.error(request, f"{p.name} is currently out of stock.")
        return redirect('product_detail', slug=p.slug)
    
    # Check current cart quantity
    cart = Cart(request)
    current_qty = cart.cart.get(str(id), {}).get('qty', 0)
    
    # Prevent adding more than available stock
    if current_qty >= p.stock:
        messages.warning(request, f"Cannot add more. Only {p.stock} items available.")
        return redirect('cart')
    
    cart.add(p.id, p.get_display_price())
    messages.success(request, f"{p.name} added to cart.")
    return redirect('cart')

@login_required
def update_cart(request,id):
    from django.contrib import messages
    product = get_object_or_404(Product, id=id)
    qty = int(request.POST['qty'])
    
    # Prevent negative quantities
    if qty < 1:
        messages.error(request, "Quantity must be at least 1.")
        return redirect('cart')
    
    # Check stock availability
    if qty > product.stock:
        messages.warning(request, f"Only {product.stock} items available for {product.name}.")
        Cart(request).update(id, product.stock)
    else:
        Cart(request).update(id, qty)
        messages.success(request, "Cart updated successfully.")
    
    return redirect('cart')

@login_required
def remove_cart(request,id):
    Cart(request).remove(id)
    return redirect('cart')

@login_required
def cart_view(request):
 cart_obj = Cart(request)
 cart = cart_obj.cart
 cart_items = []
 items_to_remove = []
 
 for id, item in cart.items():
  try:
   product = Product.objects.get(id=id)
   # Always refresh price from DB to handle started/ended campaigns
   current_price = product.get_display_price()
   item['price'] = str(current_price)
   cart_items.append({'product': product, 'qty': item['qty'], 'price': float(current_price)})
  except Product.DoesNotExist:
   items_to_remove.append(id)
 
 # Save updated prices to session
 cart_obj.save()
 
 # Remove invalid items
 for item_id in items_to_remove:
  cart_obj.remove(item_id)
 
 total = sum(float(i['price']) * i['qty'] for i in cart.values()) if cart else 0
 return render(request,'store/cart.html',{'cart_items':cart_items, 'total': total})

@login_required
@require_http_methods(["GET", "POST"])
def get_cart_count(request):
 cart = request.session.get('cart', {})
 count = sum(item['qty'] for item in cart.values()) if cart else 0
 return JsonResponse({'count': count})

@login_required
@require_http_methods(["GET"])
def get_wishlist_count(request):
    """Return wishlist count for the current user"""
    from .models import Wishlist
    count = Wishlist.objects.filter(user=request.user).count()
    return JsonResponse({'count': count})

# ============= WISHLIST VIEWS =============

@login_required
def wishlist_view(request):
    """Display user's wishlist"""
    from .models import Wishlist, RestockNotification
    from django.contrib import messages
    
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    # Prepare wishlist items with stock status and notification status
    items_with_status = []
    for item in wishlist_items:
        # Check if user is subscribed to restock notifications
        is_subscribed = RestockNotification.objects.filter(
            user=request.user,
            product=item.product,
            notified=False
        ).exists()
        
        items_with_status.append({
            'wishlist_item': item,
            'product': item.product,
            'in_stock': item.product.is_in_stock,
            'stock': item.product.stock,
            'restock_subscribed': is_subscribed
        })
    
    context = {
        'wishlist_items': items_with_status,
        'wishlist_count': wishlist_items.count()
    }
    return render(request, 'store/wishlist.html', context)

@login_required
def add_to_wishlist(request, product_id):
    """Add product to wishlist"""
    from .models import Wishlist
    from django.contrib import messages
    
    product = get_object_or_404(Product, id=product_id)
    
    # Create wishlist item (get_or_create prevents duplicates)
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if created:
        messages.success(request, f"'{product.name}' added to your wishlist!")
    else:
        messages.info(request, f"'{product.name}' is already in your wishlist.")
    
    # Redirect back to the previous page or home
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def remove_from_wishlist(request, product_id):
    """Remove product from wishlist"""
    from .models import Wishlist
    from django.contrib import messages
    
    deleted_count, _ = Wishlist.objects.filter(
        user=request.user,
        product_id=product_id
    ).delete()
    
    if deleted_count > 0:
        messages.success(request, "Product removed from wishlist!")
    else:
        messages.warning(request, "Product was not in your wishlist.")
    
    return redirect('wishlist')

@login_required
def toggle_wishlist(request, product_id):
    """Toggle product in/out of wishlist (AJAX endpoint)"""
    from .models import Wishlist
    
    product = get_object_or_404(Product, id=product_id)
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product).first()
    
    if wishlist_item:
        # Remove from wishlist
        wishlist_item.delete()
        in_wishlist = False
        message = f"'{product.name}' removed from wishlist"
    else:
        # Add to wishlist
        Wishlist.objects.create(user=request.user, product=product)
        in_wishlist = True
        message = f"'{product.name}' added to wishlist"
    
    # Get updated wishlist count
    wishlist_count = Wishlist.objects.filter(user=request.user).count()
    
    return JsonResponse({
        'success': True,
        'in_wishlist': in_wishlist,
        'message': message,
        'wishlist_count': wishlist_count
    })

@login_required
def subscribe_restock_notification(request, product_id):
    """Subscribe to restock notifications for a product"""
    from .models import RestockNotification
    from django.contrib import messages
    
    product = get_object_or_404(Product, id=product_id)
    
    # Only allow subscription for out-of-stock products
    if product.is_in_stock:
        messages.info(request, f"'{product.name}' is currently in stock. You can order it now!")
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    # Create notification subscription (get_or_create prevents duplicates)
    subscription, created = RestockNotification.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'notified': False}
    )
    
    if created:
        messages.success(request, f"You'll be notified when '{product.name}' is back in stock!")
    else:
        # Reset notification status if user re-subscribes
        if subscription.notified:
            subscription.notified = False
            subscription.notified_at = None
            subscription.save()
            messages.success(request, f"Restock notification for '{product.name}' has been reactivated!")
        else:
            messages.info(request, f"You're already subscribed to notifications for '{product.name}'.")
    
    # Redirect back to the previous page or home
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def unsubscribe_restock_notification(request, product_id):
    """Unsubscribe from restock notifications for a product"""
    from .models import RestockNotification
    from django.contrib import messages
    
    deleted_count, _ = RestockNotification.objects.filter(
        user=request.user,
        product_id=product_id
    ).delete()
    
    if deleted_count > 0:
        messages.success(request, "Restock notification cancelled.")
    else:
        messages.warning(request, "You were not subscribed to notifications for this product.")
    
    return redirect(request.META.get('HTTP_REFERER', 'wishlist'))
