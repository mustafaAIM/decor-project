from rest_framework import serializers
from order.models import Order
from service.models import ServiceOrder
from order.serializers.order_serializers import OrderItemSerializer

class CombinedOrderSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    type = serializers.SerializerMethodField()
    paid = serializers.SerializerMethodField()
    reference_number = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()
    address = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()

    def get_type(self, obj):
        data = obj['data']
        if isinstance(data, Order):
            return 'order'
        if isinstance(data, dict):  # For implementation and supervision services
            return obj['type']  # We already set this in the view
        # Get the actual model name for service orders
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