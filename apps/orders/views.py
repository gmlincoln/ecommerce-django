
import requests
import json
import hashlib
from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import get_template
from xhtml2pdf import pisa
import io
from .models import Order, OrderItem
from apps.store.models import Product
from apps.store.cart import Cart

def calculate_shipping_charge(division, district):
    """
    Calculate shipping charge based on division and district:
    - Dhaka Division, Dhaka District: 40
    - Mymensingh Division: 60
    - Chittagong Division: 120
    - Other Divisions or outside Dhaka City: 100
    """
    if division == 'Dhaka' and district == 'Dhaka':
        return 40
    elif division == 'Mymensingh':
        return 60
    elif division == 'Chittagong':
        return 120
    else:
        return 100

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart')
    
    subtotal = sum(float(i['price']) * i['qty'] for i in cart.values())
    total = subtotal  # Initialize total with subtotal as default
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'sslcommerz')
        division = request.POST.get('state')
        district = request.POST.get('city')
        
        shipping_charge = calculate_shipping_charge(division, district)
        total = float(subtotal) + shipping_charge
        
        # Create order with address information
        order = Order.objects.create(
            user=request.user, 
            total=total,
            shipping_charge=shipping_charge,
            payment_method=payment_method,
            full_name=request.POST.get('full_name'),
            phone=request.POST.get('phone'),
            email=request.POST.get('email'),
            address_line_1=request.POST.get('address_line_1'),
            address_line_2=request.POST.get('address_line_2'),
            city=district,
            state=division,
            postal_code=request.POST.get('postal_code'),
            country=request.POST.get('country', 'Bangladesh')
        )
        
        for id, item in cart.items():
            product = Product.objects.get(id=id)
            OrderItem.objects.create(
                order=order, 
                product=product, 
                quantity=item['qty'], 
                price=item['price']
            )
            
        # Clear cart immediately after order is placed
        if 'cart' in request.session:
            del request.session['cart']
            request.session.modified = True
        
        # Handle different payment methods
        if payment_method == 'cod':
            return redirect('cod_success', order_id=order.id)
        else:
            # Redirect to SSLCommerz payment
            return redirect('ssl_payment', order_id=order.id)
    
    # GET request - show checkout form
    # Get user's profile for default address
    try:
        profile = request.user.profile
        default_address = {
            'full_name': profile.full_name,
            'phone': profile.phone,
            'address_line_1': profile.address_line_1,
            'address_line_2': profile.address_line_2,
            'city': profile.city,
            'state': profile.state,
            'postal_code': profile.postal_code,
            'country': profile.country,
        }
    except:
        default_address = None
    
    context = {
        'cart_items': cart,
        'subtotal': subtotal,
        'default_address': default_address
    }
    return render(request, 'orders/checkout.html', context)

@login_required
def ssl_commerce_payment(request, order_id):
    """Initialize SSL Commerce payment"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Block payment if order is cancelled or expired
    order.check_and_cancel_if_expired()
    if order.status == 'cancelled':
        from django.contrib import messages
        from django.utils.translation import gettext as _
        messages.error(request, _("This order has been cancelled and can no longer be paid for. Please place a new order."))
        return redirect('orders')

    if order.status == 'completed':
        return redirect('orders')
    
    settings_dict = {
        'store_id': settings.SSLCOMMERZ_STORE_ID,
        'store_pass': settings.SSLCOMMERZ_STORE_PASS,
        'issandbox': True  # Assuming sandbox based on settings
    }
    
    from sslcommerz_lib.sslcommerz import SSLCOMMERZ
    sslcz = SSLCOMMERZ(settings_dict)
    
    post_body = {
        'total_amount': order.total,
        'currency': "BDT",
        'tran_id': f'ORDER_{order.id}_{order.user.id}',
        'success_url': request.build_absolute_uri('/orders/payment/success/'),
        'fail_url': request.build_absolute_uri('/orders/payment/fail/'),
        'cancel_url': request.build_absolute_uri('/orders/payment/cancel/'),
        'emi_option': 0,
        'cus_name': order.full_name or order.user.get_full_name() or order.user.username,
        'cus_email': order.email or order.user.email or 'customer@example.com',
        'cus_phone': order.phone or '01700000000',
        'cus_add1': order.address_line_1 or 'Customer Address',
        'cus_city': order.city or 'Dhaka',
        'cus_country': order.country or 'Bangladesh',
        'shipping_method': "NO",
        'multi_card_name': "",
        'num_of_item': 1,
        'product_name': f'Order #{order.order_number}',
        'product_category': "Online",
        'product_profile': "general"
    }

    try:
        response = sslcz.createSession(post_body)
        
        if response.get('status') == 'SUCCESS':
            order.transaction_id = response.get('sessionkey')
            order.save()
            return redirect(response.get('GatewayPageURL'))
        else:
            messages.error(request, f'Payment gateway error: {response.get("failedreason", "Unknown error")}')
            return redirect('checkout')
            
    except Exception as e:
        print("SSLCommerz General Error:", str(e))
        messages.error(request, f'Payment processing error: {str(e)}')
        return redirect('checkout')

@csrf_exempt
def payment_success(request):
    """Handle successful payment from SSL Commerce"""
    val_id = request.POST.get('val_id') or request.GET.get('val_id')
    # Some gateways return as POST, some GET. Ensure we check both or adapt.
    # The library might expect just val_id.
    
    if val_id:
        try:
            settings_dict = {
                'store_id': settings.SSLCOMMERZ_STORE_ID,
                'store_pass': settings.SSLCOMMERZ_STORE_PASS,
                'issandbox': True
            }
            from sslcommerz_lib.sslcommerz import SSLCOMMERZ
            sslcz = SSLCOMMERZ(settings_dict)
            
            # Identify which order this validation is for?
            # Usually we need to look up the transaction/order first so we can update it.
            # But validateTransactionOrder output usually contains tran_id.
            
            # The manual implementation relied on tran_id parameter.
            # Let's rely on validation result.
            
            validation_result = sslcz.validationTransactionOrder(val_id)
            
            if validation_result.get('status') == 'VALID' or validation_result.get('status') == 'VALIDATED':
                tran_id = validation_result.get('tran_id')
                if tran_id:
                     order_id = tran_id.split('_')[1]
                     try:
                        order = Order.objects.get(id=order_id)
                        order.status = 'completed'
                        order.transaction_id = tran_id
                        order.save()
                            
                        messages.success(request, 'Payment successful! Your order has been confirmed.')
                        return render(request, 'orders/success.html', {'order': order})
                     except Order.DoesNotExist:
                        pass
            
            messages.error(request, 'Payment validation failed.')
            return render(request, 'orders/fail.html')
            
        except Exception as e:
            print(f"Validation Error: {e}")
            messages.error(request, 'Payment validation error.')
            return render(request, 'orders/fail.html')
    
    messages.error(request, 'Invalid payment response.')
    return render(request, 'orders/fail.html')

@csrf_exempt
def payment_fail(request):
    """Handle failed payment from SSL Commerce"""
    transaction_id = request.GET.get('tran_id')
    order_id = transaction_id.split('_')[1] if transaction_id else None
    
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            # Check for expiration if payment failed
            order.check_and_cancel_if_expired()
            if order.status != 'cancelled':
                order.status = 'failed'
                order.save()
                messages.error(request, 'Payment failed. Please try again.')
            else:
                messages.error(request, 'Payment failed and the 10-minute window has expired.')
            
            return render(request, 'orders/fail.html', {'order': order})
        except Order.DoesNotExist:
            pass
    
    messages.error(request, 'Payment failed.')
    return render(request, 'orders/fail.html')

@csrf_exempt
def payment_cancel(request):
    """Handle cancelled payment from SSL Commerce"""
    transaction_id = request.GET.get('tran_id')
    order_id = transaction_id.split('_')[1] if transaction_id else None
    
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            order.status = 'cancelled'
            order.save()
            messages.warning(request, 'Payment cancelled.')
            return render(request, 'orders/cancel.html', {'order': order})
        except Order.DoesNotExist:
            pass
    
    messages.warning(request, 'Payment cancelled.')
    return render(request, 'orders/cancel.html')

@csrf_exempt
def payment_ipn(request):
    """Handle IPN (Instant Payment Notification) from SSL Commerce"""
    if request.method == 'POST':
        transaction_id = request.POST.get('tran_id')
        order_id = transaction_id.split('_')[1] if transaction_id else None
        status = request.POST.get('status')
        
        if order_id and status == 'VALID':
            try:
                order = Order.objects.get(id=order_id)
                order.status = 'completed'
                order.transaction_id = transaction_id
                order.save()
            except Order.DoesNotExist:
                pass
    
    return JsonResponse({'status': 'ok'})

@login_required
def orders(request):
    """Display user's order history"""
    orders = Order.objects.filter(user=request.user).prefetch_related('orderitem_set__product').order_by('-created_at')
    now = timezone.now()
    
    # Add payment warning info to each order
    for order in orders:
        # Check for expiration before processing
        order.check_and_cancel_if_expired()
        
        if (order.status == 'pending' and 
            order.payment_method == 'sslcommerz' and 
            order.payment_timeout and 
            order.payment_timeout > now):
            
            time_diff = order.payment_timeout - now
            minutes_remaining = int(time_diff.total_seconds() / 60)
            order.show_pay_now = True
            order.minutes_remaining = minutes_remaining
        else:
            order.show_pay_now = False
            order.minutes_remaining = 0
    
    return render(request, 'orders/orders.html', {'orders': orders, 'now': now})

@login_required
def paymentable_orders(request):
    """Display orders pending payment"""
    from django.utils import timezone
    now = timezone.now()
    
    orders = Order.objects.filter(
        user=request.user,
        status='pending',
        payment_method='sslcommerz',
        payment_timeout__gt=now
    ).prefetch_related('orderitem_set__product').order_by('payment_timeout')
    
    # Add payment warning info
    for order in orders:
        time_diff = order.payment_timeout - now
        minutes_remaining = time_diff.total_seconds() / 60
        order.show_pay_now = True
        order.minutes_remaining = int(minutes_remaining)
    
    return render(request, 'orders/orders.html', {
        'orders': orders, 
        'now': now,
        'page_title': 'Pending Payments'
    })

@login_required
def cod_success(request, order_id):
    """Handle Cash on Delivery success"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Mark order as completed for COD
    order.status = 'completed'
    order.save()
    
    return render(request, 'orders/cod_success.html', {'order': order})

@login_required
def order_tracking(request):
    """Secure order tracking view"""
    order_number = request.GET.get('order_number')
    order = None
    
    if order_number:
        try:
            # Only allow users to track their own orders
            order = Order.objects.get(order_number=order_number, user=request.user)
            # Check for expiration
            order.check_and_cancel_if_expired()
            
            # Calculate payment info for tracking page
            now = timezone.now()
            
            if (order.payment_method == 'sslcommerz' and 
                order.status == 'pending' and 
                order.payment_timeout and 
                order.payment_timeout > now):
                
                time_diff = order.payment_timeout - now
                order.minutes_remaining = int(time_diff.total_seconds() / 60)
                order.show_pay_now = True
            else:
                order.show_pay_now = False
                
        except Order.DoesNotExist:
            pass
    
    return render(request, 'orders/tracking.html', {
        'order': order,
        'order_number': order_number,
        'now': timezone.now()
    })

@login_required
def cancel_order(request, order_id):
    """Manually cancel a pending order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status == 'pending':
        order.status = 'cancelled'
        order.delivery_status = 'cancelled'
        order.save()
        messages.success(request, f'Order #{order.order_number} has been cancelled.')
    else:
        messages.error(request, 'This order cannot be cancelled.')
        
    return redirect('orders')

@login_required
def generate_invoice_pdf(request, order_id):
    """Generate professional PDF invoice"""
    # Security: Only allow users to see their own orders
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Invoice is usually for completed orders
    if order.status != 'completed' and not request.user.is_staff:
        messages.warning(request, "Invoice is available after successful payment.")
        return redirect('orders')

    template_path = 'orders/invoice_pdf.html'
    
    # Pre-format numeric values to strings to avoid template rendering issues in PDF engine
    from django.contrib.humanize.templatetags.humanize import intcomma
    
    formatted_subtotal = intcomma(order.get_subtotal())
    formatted_shipping = intcomma(order.shipping_charge)
    formatted_total = intcomma(order.total)
    
    # Also format item prices - Convert to list to ensure attributes stick
    items = list(order.orderitem_set.all())
    for item in items:
        item.formatted_price = intcomma(item.price)
        item.formatted_total = intcomma(item.get_total_price())

    import os
    from django.conf import settings
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'icon.gif')

    context = {
        'order': order,
        'items': items,
        'subtotal': formatted_subtotal,
        'shipping': formatted_shipping,
        'total': formatted_total,
        'logo_path': logo_path,
    }
    
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Invoice_{order.order_number}.pdf"'
    
    from django.template.loader import render_to_string
    html = render_to_string(template_path, context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response, encoding='utf-8')
    
    # if error then return error response
    if pisa_status.err:
       return HttpResponse(f'Error generating PDF: {pisa_status.err}<br><pre>{html}</pre>')
    
    return response
