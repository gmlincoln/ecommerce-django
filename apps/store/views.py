
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from .models import Product, Category, Campaign
from .cart import Cart
from django.utils import timezone
from django.db.models import Q

def home(request):
    query = request.GET.get('query')
    category_slug = request.GET.get('category')
    sort_by = request.GET.get('sort', 'latest')
    
    products = Product.objects.all()
    categories = Category.objects.all()
    
    # Active Campaign with products
    # Show campaigns that: are active AND haven't ended yet
    # This includes: upcoming (not started), running (started but not ended), and campaigns with NULL times
    now = timezone.now()
    campaign = Campaign.objects.filter(
        is_active=True
    ).filter(
        Q(end_time__isnull=True) | Q(end_time__gt=now)
    ).order_by('start_time').first()
    
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
    
    # Check if campaign is running (has started and not ended)
    campaign_is_running = False
    if campaign:
        now = timezone.now()
        has_started = campaign.start_time is None or campaign.start_time <= now
        has_not_ended = campaign.end_time is None or campaign.end_time > now
        campaign_is_running = has_started and has_not_ended
        
    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'campaign': campaign,
        'campaign_is_running': campaign_is_running,
        'campaign_products': campaign.products.all() if campaign and campaign_is_running else [],
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
    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related_products
    })

def campaign_detail(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    products = campaign.products.all()
    return render(request, 'store/campaign_detail.html', {
        'campaign': campaign,
        'products': products
    })

@login_required
def add_to_cart(request, id, campaign_id=None):
 p=get_object_or_404(Product,id=id)
 
 # If campaign_id is provided, use that campaign directly
 campaign = None
 if campaign_id:
     campaign = get_object_or_404(Campaign, id=campaign_id, is_active=True)
 else:
     # Otherwise, check if product is in an active running campaign to apply discount
     campaigns = Campaign.objects.filter(products=p, is_active=True)
     for c in campaigns:
         if c.is_running:
             campaign = c
             break
 
 # Use discounted price if campaign is running, otherwise use original price
 if campaign and campaign.is_running:
     discounted_price = float(p.price) * (1 - campaign.discount_percent / 100)
     Cart(request).add(p.id, discounted_price)
 else:
     Cart(request).add(p.id, p.price)
 
 return redirect('cart')

@login_required
def update_cart(request,id):
 Cart(request).update(id,int(request.POST['qty']))
 return redirect('cart')

@login_required
def remove_cart(request,id):
 Cart(request).remove(id)
 return redirect('cart')

@login_required
def cart_view(request):
 cart = request.session.get('cart',{})
 cart_items = []
 items_to_remove = []
 
 for id, item in cart.items():
  try:
   product = Product.objects.get(id=id)
   cart_items.append({'product': product, 'qty': item['qty'], 'price': float(item['price'])})
  except Product.DoesNotExist:
   items_to_remove.append(id)
 
 # Remove invalid items after iteration
 for item_id in items_to_remove:
  Cart(request).remove(item_id)
 
 total = sum(float(i['price']) * i['qty'] for i in cart.values()) if cart else 0
 return render(request,'store/cart.html',{'cart_items':cart_items, 'total': total})

@login_required
@require_http_methods(["GET", "POST"])
def get_cart_count(request):
 cart = request.session.get('cart', {})
 count = sum(item['qty'] for item in cart.values()) if cart else 0
 return JsonResponse({'count': count})
