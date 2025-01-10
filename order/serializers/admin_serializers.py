from rest_framework import serializers
from order.models import Order, OrderItem
from customer.serializers import CustomerSerializer

class AdminOrderItemSerializer(serializers.ModelSerializer):
    product_color = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = [
            'uuid',
            'product_color',
            'quantity',
            'unit_price',
            'total_price'
        ]

    def get_product_color(self, obj):
        return {
            'uuid': obj.product_color.uuid,
            'product_name': obj.product_color.product.name,
            'color_name': obj.product_color.color.hex_code,
            'price': obj.product_color.price,
            'image': obj.product_color.image.url if obj.product_color.image else None
        }

class AdminOrderSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    items = AdminOrderItemSerializer(source='items.all', many=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'uuid',
            'reference_number',
            'order_number',
            'customer',
            'status',
            'status_display',
            'phone',
            'email',
            'address',
            'city',
            'postal_code',
            'total_amount',
            'notes',
            'items',
            'created_at',
            'updated_at',
            'completed_at'
        ]

    def get_customer(self, obj):
        return {
            'id': obj.customer.id,
            'full_name': f"{obj.customer.user.first_name} {obj.customer.user.last_name}",
            'email': obj.customer.user.email,
            'phone': obj.customer.user.phone,
            'address': obj.customer.user.address
        }

class AdminOrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

    def validate_status(self, value):
        if value not in [Order.OrderStatus.PROCESSING, Order.OrderStatus.COMPLETED, 
                        Order.OrderStatus.CANCELLED, Order.OrderStatus.REFUNDED]:
            raise serializers.ValidationError("Invalid status for admin")
        return value