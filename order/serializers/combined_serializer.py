from rest_framework import serializers
from order.models import Order
from service.models import ServiceOrder
from order.serializers.order_serializers import OrderItemSerializer
from django.utils import timezone
from datetime import timedelta

class CombinedOrderSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    type = serializers.SerializerMethodField()
    paid = serializers.SerializerMethodField()
    payable = serializers.SerializerMethodField()
    reference_number = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()
    address = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    payment_uuids = serializers.SerializerMethodField()

    def get_type(self, obj):
        data = obj['data']
        if isinstance(data, Order):
            return 'order'
        if isinstance(data, dict):  # For implementation and supervision services
            return obj['type']  
        return data.content_type.model

    def get_paid(self, obj):
        data = obj['data']
        if isinstance(data, Order):
            return True
        if isinstance(data, dict):  # For implementation and supervision services
            return False  # Implementation and supervision services are not paid
        # Check service type for paid status
        service_type = data.content_type.model
        return service_type in ['designservice', 'consultingservice', 'areaservice']

    def get_reference_number(self, obj):
        data = obj['data']
        if isinstance(data, Order):
            return data.reference_number
        if isinstance(data, dict):  # For implementation and supervision services
            return data['service_number']
        return data.service_number

    def get_status(self, obj):
        data = obj['data']
        if isinstance(data, Order):
            return data.status
        if isinstance(data, dict):  # For implementation and supervision services
            return data['status']
        return data.status

    def get_address(self, obj):
        data = obj['data']
        if isinstance(data, Order):
            return data.address
        if isinstance(data, dict):  # For implementation and supervision services
            return data['service'].address
        return data.service.address if hasattr(data.service, 'address') else None

    def get_phone(self, obj):
        data = obj['data']
        if isinstance(data, Order):
            return data.phone
        if isinstance(data, dict):  # For implementation and supervision services
            return data['service'].phone_number
        return data.service.phone_number if hasattr(data.service, 'phone_number') else None

    def get_email(self, obj):
        data = obj['data']
        if isinstance(data, Order):
            return data.email
        if isinstance(data, dict):  # For implementation and supervision services
            return data['service'].email
        return data.service.email if hasattr(data.service, 'email') else None

    def get_city(self, obj):
        data = obj['data']
        if isinstance(data, Order):
            return data.city
        if isinstance(data, dict):  # For implementation and supervision services
            return data['service'].city
        return data.service.city if hasattr(data.service, 'city') else None

    def get_notes(self, obj):
        data = obj['data']
        if isinstance(data, Order):
            return data.notes
        if isinstance(data, dict):  # For implementation and supervision services
            return data['service'].notes
        return data.service.notes if hasattr(data.service, 'notes') else None

    def get_items(self, obj):
        data = obj['data']
        if isinstance(data, Order):
            return OrderItemSerializer(data.items.all(), many=True).data
        return None 

    def get_amount(self, obj):
        data = obj['data']
        if isinstance(data, Order):
            return float(data.total_amount)
        if isinstance(data, dict):  
            return 0  
        return float(data.amount) if hasattr(data, 'amount') else 0 

    def get_payment_uuids(self, obj):
        data = obj['data']
        if isinstance(data, Order) or isinstance(data, ServiceOrder):
            return str(data.payments.order_by('created_at').last().uuid) if data.payments.order_by('created_at').last() else None
        return None

    def get_payable(self, obj):
        data = obj['data']
        if isinstance(data, dict):  
            return False
        created_at = data.created_at
        time_difference = timezone.now() - created_at
        return time_difference.total_seconds() <= 24 * 3600 