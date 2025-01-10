from django.urls import path
from order.views import OrderViewSet, CombinedOrderViewSet, AdminOrderViewSet

urlpatterns = [
    path('orders/', OrderViewSet.as_view({'get': 'list'}), name='order-list'),
    path('orders/count/', OrderViewSet.as_view({'get': 'count'}), name='order-count'),
    path('order/create/', OrderViewSet.as_view({'post': 'create_order'}), name='order-create'),
    path('order/<uuid:uuid>/', OrderViewSet.as_view({
        'get': 'retrieve',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='order-detail'),
    path('combined-orders/', CombinedOrderViewSet.as_view({'get': 'list'}), name='combined-orders'),
    path('admin/orders/', AdminOrderViewSet.as_view({'get': 'list'}), name='admin-order-list'),
    path('admin/orders/<uuid:uuid>/', AdminOrderViewSet.as_view({
        'get': 'retrieve',
        'patch': 'change_status'
    }), name='admin-order-detail'),
] 