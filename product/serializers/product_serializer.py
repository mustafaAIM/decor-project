# django
from django.db import models
# rest framework
from rest_framework import serializers

from utils.shortcuts import get_object_or_404
# models
from ..models.product_model import Product
from ..models.rate_model import Rate
from section.models.category_model import Category
# serializers
from .product_color_serializer import ProductColorSerializer

class ProductSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField(read_only=True)
    category = serializers.UUIDField()

    class Meta:
        model = Product
        fields = ['uuid', 'name', 'image', 'category', 'average_rating']
    
    def get_average_rating(self, obj):
        ratings = Rate.objects.filter(product=obj)
        average = ratings.aggregate(models.Avg('score'))['score__avg']
        return average if average is not None else 0.0 