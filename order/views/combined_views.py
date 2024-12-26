from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from django.db.models import Q
from itertools import chain
from operator import attrgetter

from order.models import Order
from service.models import ServiceOrder
from order.serializers.combined_serializer import CombinedOrderSerializer
from utils import ResponseFormatter
from customer.permissions import IsCustomer

class CombinedOrderViewSet(ViewSet):
    permission_classes = [IsCustomer]

    def list(self, request):
        orders = Order.objects.filter(
            customer=request.user.customer
        ).select_related(
            'customer'
        ).prefetch_related(
            'items__product_color__product',
            'items__product_color__color'
        )

        service_orders = ServiceOrder.objects.filter(
            customer=request.user.customer
        ).select_related(
            'customer',
            'content_type'
        )

        combined_orders = sorted(
            chain(orders, service_orders),
            key=attrgetter('created_at'),
            reverse=True
        )

        serialized_data = []
        for item in combined_orders:
            if isinstance(item, Order):
                data = {
                    'type': 'product_order',
                    'data': item,
                    'created_at': item.created_at
                }
            else:  
                data = {
                    'type': f'service_order_{item.content_type.model}',
                    'data': item,
                    'created_at': item.created_at
                }
            serialized_data.append(data)

        serializer = CombinedOrderSerializer(serialized_data, many=True)
        
        return ResponseFormatter.success_response(
            data=serializer.data
        ) 