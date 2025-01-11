# django
from django.shortcuts import get_object_or_404
# rest framework
from rest_framework import serializers
# models
from ..models.product_model import Product
from ..models.color_model import Color
from ..models.product_color_model import ProductColor
from section.models.category_model import Category

class ProductUpdateSerializer(serializers.ModelSerializer):
    category = serializers.UUIDField(required=False)
    hex_codes = serializers.ListField(
        child=serializers.CharField(max_length=255),
        required=False
    )
    prices = serializers.ListField(
        child=serializers.DecimalField(max_digits=10, decimal_places=2),
        required=False
    )
    quantities = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=False
    )

    class Meta:
        model = Product
        fields = ['uuid', 'name', 'description', 'image', 'category', 'hex_codes', 'prices', 'quantities', 'images']

    def update(self, instance, validated_data):
        hex_codes = validated_data.pop('hex_codes', [])
        prices = validated_data.pop('prices', [])
        quantities = validated_data.pop('quantities', [])
        images = validated_data.pop('images', [])

        category_uuid = validated_data.pop('category', None)
        
        if category_uuid:
            category = get_object_or_404(Category, uuid=category_uuid)
        else:
            category = instance.category
        
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.image = validated_data.get('image', instance.image)
        instance.category = category
        instance.save()

        if (len(hex_codes) != len(prices)) or (len(hex_codes) != len(quantities)) or (len(hex_codes) != len(images)):
            raise serializers.ValidationError("hex_codes, prices, quantities, and images must have the same length.")

        existing_colors = {pc.color.hex_code: pc for pc in instance.product_colors.all()}
        for hex_code, price, quantity, image in zip(hex_codes, prices, quantities, images):
            if hex_code in list(existing_colors.keys()):
                product_color = existing_colors[hex_code]
                # product_color.price = price
                product_color.quantity = quantity
                # product_color.image = image
                product_color.save()
            else:
                color = Color.objects.create(hex_code=hex_code)
                ProductColor.objects.create(
                    product=instance,
                    color=color,
                    price=price,
                    quantity=quantity,
                    image=image
                )

        return instance