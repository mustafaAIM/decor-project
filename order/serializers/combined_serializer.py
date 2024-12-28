from rest_framework import serializers
from order.models import Order
from service.models import ServiceOrder
from order.serializers.order_serializers import OrderItemSerializer

class CombinedOrderSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    type = serializers.CharField()
    reference_number = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()
    address = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()

    def get_reference_number(self, obj):
        data = obj['data']
        if isinstance(data, Order):
            return data.reference_number
        return data.service_number

    def get_status(self, obj):
        data = obj['data']
        if isinstance(data, Order):
            return data.status
        return data.status

    def get_address(self, obj):
        data = obj['data']
        print(data)
        if isinstance(data, Order):
            return data.address
        return data.address if hasattr(data, 'address') else None

    def get_phone(self, obj):
        data = obj['data']
        if isinstance(data, Order):
            return data.phone
        return data.phone_number if hasattr(data, 'phone_number') else None

    def get_email(self, obj):
        data = obj['data']
        if isinstance(data, Order):
            return data.email
        return data.email if hasattr(data, 'email') else None

    def get_city(self, obj):
        data = obj['data']
        if isinstance(data, Order):
            return data.city
        return data.city if hasattr(data, 'city') else None

    def get_notes(self, obj):
        data = obj['data']
        if isinstance(data, Order):
            return data.notes
        return data.notes if hasattr(data, 'notes') else None

    def get_items(self, obj):
        data = obj['data']
        if isinstance(data, Order):
            return OrderItemSerializer(data.items.all(), many=True).data
        return None 