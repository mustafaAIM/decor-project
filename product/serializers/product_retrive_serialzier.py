# django
from django.db import models
# rest framework
from rest_framework import serializers
# models
from ..models.product_model import Product
from ..models.rate_model import Rate
# serializers
from .product_color_serializer import ProductColorSerializer
from section.serializers.category_serializers import CategorySerializer

class ProductRetrieveSerializer(serializers.ModelSerializer):
    product_colors = ProductColorSerializer(source="product_colors.all", many=True)
    average_rating = serializers.SerializerMethodField(read_only=True)
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = ['uuid', 'name', 'description', 'image', 'category', 'product_colors', 'average_rating']

    def get_average_rating(self, obj):
        ratings = Rate.objects.filter(product=obj)
        average = ratings.aggregate(models.Avg('score'))['score__avg']
        return average if average is not None else 0.0
