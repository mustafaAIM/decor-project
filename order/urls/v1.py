from django.urls import path
from order.views import OrderViewSet

urlpatterns = [
    path('order/create/', OrderViewSet.as_view({'post': 'create_order'}), name='order-create'),
    path('order/<uuid:uuid>/', OrderViewSet.as_view({
        'get': 'retrieve',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='order-detail'),
    path('orders/', OrderViewSet.as_view({'get': 'list'}), name='order-list'),
] 