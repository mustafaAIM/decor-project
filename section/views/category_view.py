#rest
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

#models 
from section.models import Category
#serializers
from section.serializers import CategorySerializer


class CategoryViewSet(ModelViewSet):
      queryset = Category.objects.all()
      serializer_class = CategorySerializer
      