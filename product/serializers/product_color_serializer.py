# django
from django.core.exceptions import ValidationError
# rest_framework
from rest_framework import serializers
# models
from ..models.color_model import Color
from ..models.product_color_model import ProductColor
# utils
from ..utils.response import custom_message
# serializers
from .color_serializer import ColorSerializer

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
            raise serializers.ValidationError("Price must be a positive number.")
        return value

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity must be a positive number.")
        return value