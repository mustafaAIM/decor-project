#rest
from rest_framework import viewsets, status
from rest_framework.response import Response
#filter
from section.filters import CategoryFilter
#models 
from section.models import Category
#serializers
from section.serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.select_related('section')
    serializer_class = CategorySerializer
    lookup_field = 'uuid'
    filterset_class = CategoryFilter
    
    def get_queryset(self):
        queryset = super().get_queryset()
        section_name = self.request.query_params.get('section_name', None)
        if section_name is not None:
            queryset = queryset.filter(section__name__icontains=section_name)
        return queryset

    