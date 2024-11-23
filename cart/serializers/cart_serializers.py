from rest_framework import serializers
from cart.models import Cart, CartItem
from product.models.product_color_model import ProductColor
from utils.api_exceptions import BadRequestError, NotFoundError
from utils.shortcuts import get_object_or_404

class CartItemSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True)
    product_uuid = serializers.UUIDField(source='product_color.product.uuid', read_only=True)
    product_name = serializers.CharField(source='product_color.product.name', read_only=True)
    product_image = serializers.ImageField(source='product_color.product.image', read_only=True)
    color_hex = serializers.CharField(source='product_color.color.hex_code', read_only=True)
    price = serializers.DecimalField(source='product_color.price', max_digits=10, decimal_places=2, read_only=True)
    subtotal = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)

    class Meta:
        model = CartItem
        fields = [
            'uuid', 'product_uuid', 'product_name', 'product_image',
            'color_hex', 'quantity', 'price', 'subtotal'
        ]

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)

    class Meta:
        model = Cart
        fields = ['uuid', 'items', 'total_items', 'subtotal', 'created_at', 'updated_at']
        read_only_fields = ['uuid', 'created_at', 'updated_at']


class AddToCartSerializer(serializers.Serializer):
    product_color_uuid = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, data):
        product_color = get_object_or_404(ProductColor, uuid=data['product_color_uuid'])
        if data['quantity'] > product_color.quantity:
            raise BadRequestError(
                en_message=f"Only {product_color.quantity} items available in stock",
                ar_message=f"يتوفر فقط {product_color.quantity} قطع في المخزون"
            )

        data['product_color'] = product_color
        return data

class UpdateCartItemSerializer(serializers.Serializer):
    item_uuid = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=0)

    def validate(self, data):
        cart_item = get_object_or_404(CartItem, uuid=data['item_uuid'])
        if data['quantity'] > cart_item.product_color.quantity:
            raise BadRequestError(
                en_message=f"Only {cart_item.product_color.quantity} items available in stock",
                ar_message=f"يتوفر فقط {cart_item.product_color.quantity} قطع في المخزون"
            )
        data['cart_item'] = cart_item
        return data

class RemoveCartItemSerializer(serializers.Serializer):
    item_uuid = serializers.UUIDField()
    def validate_item_uuid(self, value):
        cart = self.context['cart']
        get_object_or_404(cart.items,uuid=value)
        return value