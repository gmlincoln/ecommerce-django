
from django.urls import path
from .views import *

urlpatterns=[
 path('', home, name='home'),
 path('add/<int:id>/', add_to_cart, name='add_to_cart'),
 path('cart/', cart_view, name='cart'),
 path('update/<int:id>/', update_cart, name='update_cart'),
 path('remove/<int:id>/', remove_cart, name='remove_cart'),
 path('cart/count/', get_cart_count, name='cart_count'),
 path('wishlist/count/', get_wishlist_count, name='wishlist_count'),
 path('product/<slug:slug>/', product_detail, name='product_detail'),
 path('product/item/<int:id>/', product_detail, name='product_detail_id'),
 path('campaign/<int:campaign_id>/', campaign_detail, name='campaign_detail'),
 
 # Wishlist URLs
 path('wishlist/', wishlist_view, name='wishlist'),
 path('wishlist/add/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
 path('wishlist/remove/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
 path('wishlist/toggle/<int:product_id>/', toggle_wishlist, name='toggle_wishlist'),
 
 # Restock Notification URLs
 path('restock/subscribe/<int:product_id>/', subscribe_restock_notification, name='subscribe_restock'),
 path('restock/unsubscribe/<int:product_id>/', unsubscribe_restock_notification, name='unsubscribe_restock'),
]
