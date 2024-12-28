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
        # Get regular orders
        orders = Order.objects.filter(
            customer=request.user.customer
        ).select_related(
            'customer'
        ).prefetch_related(
            'items__product_color__product',
            'items__product_color__color'
        )

        # Get service orders
        service_orders = ServiceOrder.objects.filter(
            customer=request.user.customer
        ).select_related(
            'customer',
            'content_type'
        )

        # Combine and sort both types of orders
        combined_orders = sorted(
            chain(orders, service_orders),
            key=attrgetter('created_at'),
            reverse=True
        )

        # Prepare the data with simplified type information
        serialized_data = []
        for item in combined_orders:
            if isinstance(item, Order):
                data = {
                    'uuid': item.uuid,
                    'type': 'order',
                    'data': item,
                    'created_at': item.created_at
                }
            else:  # ServiceOrder
                data = {
                    'uuid': item.uuid,
                    'type': 'service',
                    'data': item,
                    'created_at': item.created_at
                }
            serialized_data.append(data)

        serializer = CombinedOrderSerializer(serialized_data, many=True)
        
        return ResponseFormatter.success_response(
            data=serializer.data
        ) 