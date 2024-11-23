# django
from django.db import models
# rest frameword
from rest_framework import serializers
# models
from ..models.product_model import Product
from ..models.rate_model import Rate
from ..models.product_color_model import ProductColor
from ..models.color_model import Color
# serializers
from .product_color_serializer import ProductColorSerializer

class ProductDetailSerializer(serializers.ModelSerializer):
    product_colors = ProductColorSerializer(many=True)
    average_rating = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = ['uuid', 'name', 'description', 'image', 'product_colors', 'average_rating']

    def get_average_rating(self, obj):
        ratings = Rate.objects.filter(product=obj)
        average = ratings.aggregate(models.Avg('score'))['score__avg']
        return average if average is not None else 0.0
    
    def update(self, instance, validated_data):
        product_colors_data = validated_data.pop('product_colors', [])
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        for product_color_data in product_colors_data:
            color_data = product_color_data.pop('color')
            color, _ = Color.objects.get_or_create(**color_data)
            product_color, created = ProductColor.objects.update_or_create(
                product=instance,
                color=color,
                defaults=product_color_data
            )
        return instance