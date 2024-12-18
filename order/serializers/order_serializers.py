from rest_framework import serializers
from django.db.models import Sum, F
from ..models import Order, OrderItem
from utils import BadRequestError

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['uuid', 'product_color', 'quantity', 'unit_price', 'total_price']
        read_only_fields = ['uuid', 'total_price']

    def validate_quantity(self, value):
        if value <= 0:
            raise BadRequestError(
                en_message="Quantity must be greater than zero",
                ar_message="يجب أن تكون الكمية أكبر من صفر"
            )
        return value

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'uuid', 'reference_number', 'customer', 'order_number',
            'status', 'total_amount', 'notes', 'items',
            'phone', 'email', 'address', 'city', 'postal_code',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['uuid', 'reference_number', 'status', 'created_at', 'updated_at', 'completed_at']

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['customer', 'notes', 'items']

    def validate_items(self, value):
        if not value:
            raise BadRequestError(
                en_message="Order must contain at least one item",
                ar_message="يجب أن يحتوي الطلب على عنصر واحد على الأقل"
            )
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(
            **validated_data,
            total_amount=0
        )
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        total_amount = OrderItem.objects.filter(order=order).aggregate(
            total=Sum(F('quantity') * F('unit_price'))
        )['total'] or 0

        order.total_amount = total_amount
        order.save()

        return order 