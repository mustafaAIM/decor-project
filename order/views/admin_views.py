from rest_framework import viewsets
from admin.permissions import IsAdmin
from django_filters import rest_framework as filters
from django.db.models import Q
from order.models import Order
from order.serializers.admin_serializers import AdminOrderSerializer, AdminOrderStatusSerializer
from utils import ResponseFormatter, BadRequestError
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework import status as http_status

class OrderFilter(filters.FilterSet):
    # Status filters
    status = filters.ChoiceFilter(choices=Order.OrderStatus.choices)
    
    # Date filters
    created_at_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    date_range = filters.CharFilter(method='filter_date_range')
    
    # Customer filters
    customer_name = filters.CharFilter(method='filter_customer_name')
    customer_phone = filters.CharFilter(method='filter_customer_phone')
    customer_email = filters.CharFilter(field_name='customer__user__email', lookup_expr='icontains')
    
    # Order filters
    reference_number = filters.CharFilter(lookup_expr='icontains')
    min_amount = filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    max_amount = filters.NumberFilter(field_name='total_amount', lookup_expr='lte')
    city = filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Order
        fields = [
            'status', 'created_at_after', 'created_at_before', 'customer_name',
            'customer_phone', 'customer_email', 'reference_number', 'min_amount',
            'max_amount', 'city', 'date_range'
        ]

    def filter_customer_name(self, queryset, name, value):
        return queryset.filter(
            Q(customer__user__first_name__icontains=value) |
            Q(customer__user__last_name__icontains=value)
        )

    def filter_customer_phone(self, queryset, name, value):
        return queryset.filter(
            Q(customer__phone__icontains=value) |
            Q(phone__icontains=value)
        )

    def filter_date_range(self, queryset, name, value):
        today = timezone.now()
        
        if value == 'today':
            start_date = today.replace(hour=0, minute=0, second=0)
            end_date = today.replace(hour=23, minute=59, second=59)
        elif value == 'yesterday':
            start_date = (today - timedelta(days=1)).replace(hour=0, minute=0, second=0)
            end_date = (today - timedelta(days=1)).replace(hour=23, minute=59, second=59)
        elif value == 'this_week':
            start_date = (today - timedelta(days=today.weekday())).replace(hour=0, minute=0, second=0)
            end_date = today.replace(hour=23, minute=59, second=59)
        elif value == 'this_month':
            start_date = today.replace(day=1, hour=0, minute=0, second=0)
            end_date = today.replace(hour=23, minute=59, second=59)
        else:
            return queryset

        return queryset.filter(created_at__range=(start_date, end_date))

class AdminOrderViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = AdminOrderSerializer
    filterset_class = OrderFilter
    lookup_field = 'uuid'
    pagination_class = None

    def get_queryset(self):
        return Order.objects.filter(
            status__in=[Order.OrderStatus.PROCESSING, Order.OrderStatus.COMPLETED]
        ).select_related(
            'customer',
            'customer__user'
        ).prefetch_related(
            'items__product_color__product',
            'items__product_color__color'
        ).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return ResponseFormatter.success_response(
            data=serializer.data
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ResponseFormatter.success_response(
            data=serializer.data
        )

    @action(detail=True, methods=['patch'])
    def change_status(self, request, uuid=None):
        instance = self.get_object()
        serializer = AdminOrderStatusSerializer(instance, data=request.data, partial=True)
        
        if not serializer.is_valid():
            raise BadRequestError(
                en_message="Invalid status",
                ar_message="حالة غير صالحة"
            )

        # Check if the status transition is valid
        new_status = serializer.validated_data['status']
        current_status = instance.status

        # Define valid status transitions
        valid_transitions = {
            Order.OrderStatus.PENDING: [Order.OrderStatus.PROCESSING, Order.OrderStatus.CANCELLED],
            Order.OrderStatus.PROCESSING: [Order.OrderStatus.COMPLETED, Order.OrderStatus.CANCELLED],
            Order.OrderStatus.COMPLETED: [Order.OrderStatus.REFUNDED],
            Order.OrderStatus.CANCELLED: [],  # No transitions allowed from CANCELLED
            Order.OrderStatus.REFUNDED: [],   # No transitions allowed from REFUNDED
        }

        if new_status not in valid_transitions.get(current_status, []):
            raise BadRequestError(
                en_message=f"Cannot change status from {current_status} to {new_status}",
                ar_message=f"لا يمكن تغيير الحالة من {current_status} إلى {new_status}"
            )

        # Update the status
        instance = serializer.save()
        
        # If status is changed to COMPLETED, set completed_at
        if new_status == Order.OrderStatus.COMPLETED:
            instance.completed_at = timezone.now()
            instance.save()

        return ResponseFormatter.success_response(
            data=AdminOrderSerializer(instance).data,
        )