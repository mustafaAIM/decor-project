# django
from django.db import models
# rest framework
from rest_framework import serializers
# models
from ..models.product_model import Product
from ..models.rate_model import Rate
# serializers
from .product_color_serializer import ProductColorSerializer

class ProductSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = ['uuid', 'name', 'image','category', 'average_rating']
    
    def get_average_rating(self, obj):
        ratings = Rate.objects.filter(product=obj)
        average = ratings.aggregate(models.Avg('score'))['score__avg']
        return average if average is not None else 0.0 

    def create(self, validated_data):
        product_colors_data = validated_data.pop('product_colors', [])
        product = Product.objects.create(**validated_data)
        for product_color_data in product_colors_data:
            serializer = ProductColorSerializer(data=product_color_data)
            serializer.is_valid(raise_exception=True) 
            serializer.save(product=product) 
        return product