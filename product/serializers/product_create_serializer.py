# django
from django.shortcuts import get_object_or_404
# rest framework
from rest_framework import serializers
# models
from ..models.product_model import Product
from ..models.rate_model import Rate
from section.models.category_model import Category
# serializers
from .product_color_serializer import ProductColorSerializer

class ProductCreateSerializer(serializers.ModelSerializer):
    category = serializers.UUIDField()

    class Meta:
        model = Product
        fields = ['uuid', 'name', 'description', 'image', 'category']

    def create(self, validated_data):
        product_colors_data = self.context['request'].data.get('product_colors', [])
        category_uuid = validated_data.pop('category')
        category = get_object_or_404(Category, uuid=category_uuid)
        product = Product.objects.create(category=category, **validated_data)

        for product_color_data in product_colors_data:
            serializer = ProductColorSerializer(data=product_color_data)
            serializer.is_valid(raise_exception=True)
            serializer.save(product=product)

        return product