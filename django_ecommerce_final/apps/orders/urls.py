
from django.urls import path
from .views import checkout, ssl_commerce_payment, cod_success, orders, payment_success, payment_fail, payment_cancel, payment_ipn, paymentable_orders, order_tracking, cancel_order, generate_invoice_pdf

urlpatterns=[
    path('checkout/', checkout, name='checkout'),
    path('tracking/', order_tracking, name='order_tracking'),
    path('payment/paymentable/', paymentable_orders, name='paymentable_orders'),
    path('payment/<int:order_id>/', ssl_commerce_payment, name='ssl_payment'),
    path('cod-success/<int:order_id>/', cod_success, name='cod_success'),
    path('', orders, name='orders'),
    path('cancel/<int:order_id>/', cancel_order, name='cancel_order'),
    path('payment/success/', payment_success, name='payment_success'),
    path('payment/fail/', payment_fail, name='payment_fail'),
    path('payment/cancel/', payment_cancel, name='payment_cancel'),
    path('payment/ipn/', payment_ipn, name='payment_ipn'),
    path('invoice/<int:order_id>/', generate_invoice_pdf, name='generate_invoice_pdf'),
]
