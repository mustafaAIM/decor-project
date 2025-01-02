# django
from django.shortcuts import get_object_or_404
# rest framework
from rest_framework import serializers
# models
from ..models.product_model import Product
from section.models.category_model import Category
from product.models.color_model import Color
from product.models.product_color_model import ProductColor
# utile
from utils.api_exceptions import BadRequestError

class ProductCreateSerializer(serializers.ModelSerializer):
    category = serializers.UUIDField()
    hex_codes = serializers.ListField(
        child=serializers.CharField(max_length=255),
        write_only=True,
        required=True
    )
    prices = serializers.ListField(
        child=serializers.DecimalField(max_digits=10, decimal_places=2),
        write_only=True,
        required=True
    )
    quantities = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=True
    )
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True
    )

    class Meta:
        model = Product
        fields = ['uuid', 'name', 'description', 'image', 'category', 'hex_codes', 'prices', 'quantities', 'images']

    def create(self, validated_data):
        hex_codes = validated_data.pop('hex_codes', [])
        prices = validated_data.pop('prices', [])
        quantities = validated_data.pop('quantities', [])
        images = validated_data.pop('images', [])

        if not hex_codes or not prices or not quantities:
            raise BadRequestError(
                en_message="hex_codes, prices, and quantityes fields are required.",
                ar_message="كود اللون والاسعار والكميات مطلوبة للمنتج."
            )

        if (not (len(hex_codes) == len(prices) == len(quantities))) or (len(hex_codes) < len(images)):
            raise BadRequestError(
                en_message="hex_codes, prices, and quantities lists must have the same length.",
                ar_message="كود اللون والاسعار والكميات يجب ان تكون بنفس الطول."
            )

        category_uuid = validated_data.pop('category')
        category = get_object_or_404(Category, uuid=category_uuid)
        product = Product.objects.create(category=category, **validated_data)

        for hex_code, price, quantity, image in zip(hex_codes, prices, quantities, images):
            color, _ = Color.objects.get_or_create(hex_code=hex_code)
            ProductColor.objects.create(product=product, color=color, price=price, quantity=quantity, image=image)
            
        return product