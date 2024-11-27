from django.urls import path
from cart.views.cart_view import (
    CartListView,
    CartItemCreateView,
    CartItemDestroyUpdateView,
    CartClearView
)

urlpatterns = [
    path('cart/', CartListView.as_view(), name='cart-list'),
    
    path('cart/items/', CartItemCreateView.as_view(), name='cart-item-create'),
    
    path('cart/item/<uuid:item_uuid>/', 
         CartItemDestroyUpdateView.as_view(), 
         name='cart-item-update'),
         
    path('cart/clear/', 
         CartClearView.as_view(), 
         name='cart-clear'),
]