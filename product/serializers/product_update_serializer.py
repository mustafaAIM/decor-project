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
    quantities = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )

    class Meta:
        model = Product
        fields = ['uuid', 'name', 'description', 'image', 'category', 'hex_codes', 'quantities']

    def update(self, instance, validated_data):
        hex_codes = validated_data.pop('hex_codes', [])
        quantities = validated_data.pop('quantities', [])

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

        if (len(hex_codes) != len(quantities)):
            raise serializers.ValidationError("hex_codes and quantities must have the same length.")

        existing_colors = {pc.color.hex_code: pc for pc in instance.product_colors.all()}
        for hex_code, quantity in zip(hex_codes, quantities):
            if hex_code in list(existing_colors.keys()):
                product_color = existing_colors[hex_code]
                product_color.quantity = quantity
                product_color.save()

        return instance