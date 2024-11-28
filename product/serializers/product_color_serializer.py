# rest_framework
from rest_framework import serializers
# models
from ..models.color_model import Color
from ..models.product_color_model import ProductColor
# serializers
from .color_serializer import ColorSerializer
# utile
from utils.api_exceptions import BadRequestError

class ProductColorSerializer(serializers.ModelSerializer):
    color = ColorSerializer()

    class Meta:
        model = ProductColor
        fields = ['uuid', 'color', 'price', 'quantity']

    def create(self, validated_data):
        color_data = validated_data.pop('color')
        color, _ = Color.objects.get_or_create(**color_data)
        product_color = ProductColor.objects.create(color=color, **validated_data)
        return product_color
    
    def validate_price(self, value):
        if value < 0:
            raise BadRequestError(en_message="Price must be a positive number.", ar_message="السعر يجب أن يكون قيمة موجبة", status_code=400)
        return value
    def validate_quantity(self, value):
        if value < 0:
            raise BadRequestError(en_message="Quantity must be a positive number.", ar_message="الكمية يجب أن تكون قيمة موجبة", status_code=400)
        return value