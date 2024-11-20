#rest
from rest_framework import serializers
#models 
from section.models import Category , Section

class CategorySerializer(serializers.ModelSerializer):
     class Meta:
          model = Category
          fields = "__all__"