# django
from django.db import models
# rest framework
from rest_framework import serializers

from utils.shortcuts import get_object_or_404
# models
from ..models.product_model import Product
from ..models.rate_model import Rate
from section.models.category_model import Category
from ..models.product_color_model import ProductColor
# serializers
from .product_color_serializer import ProductColorSerializer

class ProductSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField(read_only=True)
    category = serializers.UUIDField()
    price = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['uuid', 'name', 'image', 'category', 'price', 'average_rating']
    
    def get_average_rating(self, obj):
        ratings = Rate.objects.filter(product=obj)
        average = ratings.aggregate(models.Avg('score'))['score__avg']
        return average if average is not None else 0.0 
    
    def get_price(self, obj):
        product_color = obj.product_colors.first()
        return product_color.price if product_color.price else None