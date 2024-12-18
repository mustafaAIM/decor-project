from django.urls import path
from cart.views.cart_view import (
    CartViewSet,
    CartItemCreateView,
    CartItemDestroyUpdateView,
    CartClearView
)

urlpatterns = [
    path('cart/', CartViewSet.as_view({'get': 'list'}), name='cart-list'),
    path('cart/count/', CartViewSet.as_view({'get': 'count'}), name='cart-count'),
    path('cart/items/', CartItemCreateView.as_view(), name='cart-item-create'),
    path('cart/item/<uuid:item_uuid>/', 
         CartItemDestroyUpdateView.as_view(), 
         name='cart-item-update'),
    path('cart/clear/', 
         CartClearView.as_view(), 
         name='cart-clear'),
]