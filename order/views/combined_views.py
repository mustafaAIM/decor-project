from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from itertools import chain
from operator import attrgetter

from order.models import Order
from service.models import ServiceOrder
from service.models.impementaion_service_model import ImplementaionService
from service.models.supervision_service_model import SupervisionService
from order.serializers.combined_serializer import CombinedOrderSerializer
from utils import ResponseFormatter
from customer.permissions import IsCustomer

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CombinedOrderViewSet(ViewSet):
    permission_classes = [IsCustomer]
    pagination_class = StandardResultsSetPagination

    def get_paginated_response(self, data):
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(data, self.request)
        if page is not None:
            serializer = CombinedOrderSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        serializer = CombinedOrderSerializer(data, many=True)
        return Response(serializer.data)

    def list(self, request):
        # Get regular orders
        orders = Order.objects.filter(
            customer=request.user.customer
        ).select_related(
            'customer'
        ).prefetch_related(
            'items__product_color__product',
            'items__product_color__color',
            'payments'
        )

        # Get paid service orders (design, consulting, area)
        service_orders = ServiceOrder.objects.filter(
            customer=request.user.customer
        ).select_related(
            'customer',
            'content_type'
        ).prefetch_related(
            'payments'
        )

        # Get implementation services (direct, no ServiceOrder)
        implementation_services = ImplementaionService.objects.filter(
            customer=request.user.customer
        ).select_related(
            'customer',
            'section'
        )

        # Get supervision services (direct, no ServiceOrder)
        supervision_services = SupervisionService.objects.filter(
            customer=request.user.customer
        ).select_related(
            'customer',
            'section'
        )

        # Prepare the data with type information
        serialized_data = []
        
        # Add regular orders
        for order in orders:
            serialized_data.append({
                'uuid': order.uuid,
                'type': 'order',
                'data': order,
                'created_at': order.created_at
            })

        # Add paid service orders
        for service_order in service_orders:
            serialized_data.append({
                'uuid': service_order.uuid,
                'type': service_order.content_type.model,
                'data': service_order,
                'created_at': service_order.created_at
            })

        # Add implementation services
        for impl_service in implementation_services:
            serialized_data.append({
                'uuid': impl_service.uuid,
                'type': 'implementationservice',
                'data': {
                    'uuid': impl_service.uuid,
                    'status': 'PENDING',  # Default status since these don't have ServiceOrder
                    'service': impl_service,
                    'service_number': f'IMPL-{impl_service.uuid.hex[:8]}'
                },
                'created_at': impl_service.created_at
            })

        # Add supervision services
        for super_service in supervision_services:
            serialized_data.append({
                'uuid': super_service.uuid,
                'type': 'supervisionservice',
                'data': {
                    'uuid': super_service.uuid,
                    'status': 'PENDING',  # Default status since these don't have ServiceOrder
                    'service': super_service,
                    'service_number': f'SUP-{super_service.uuid.hex[:8]}'
                },
                'created_at': super_service.created_at
            })

        # Sort all items by created_at
        serialized_data.sort(key=lambda x: x['created_at'], reverse=True)

        # Apply pagination and return response
        paginated_response = self.get_paginated_response(serialized_data)
        
        return ResponseFormatter.success_response(
            data={
                'count': paginated_response.data['count'],
                'next': paginated_response.data['next'],
                'previous': paginated_response.data['previous'],
                'results': paginated_response.data['results']
            }
        ) 