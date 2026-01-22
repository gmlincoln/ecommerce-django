
from django.urls import path
from .views import *

urlpatterns=[
 path('', home, name='home'),
 path('add/<int:id>/', add_to_cart, name='add_to_cart'),
 path('add/<int:id>/<int:campaign_id>/', add_to_cart, name='add_to_cart_campaign'),
 path('cart/', cart_view, name='cart'),
 path('update/<int:id>/', update_cart, name='update_cart'),
 path('remove/<int:id>/', remove_cart, name='remove_cart'),
 path('cart/count/', get_cart_count, name='cart_count'),
 path('product/<slug:slug>/', product_detail, name='product_detail'),
 path('product/item/<int:id>/', product_detail, name='product_detail_id'),
 path('campaign/<int:campaign_id>/', campaign_detail, name='campaign_detail'),
]
