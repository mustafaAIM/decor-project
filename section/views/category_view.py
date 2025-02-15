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
        section_title = self.request.query_params.get('section_title', None)
        if section_title is not None:
            queryset = queryset.filter(section__title__icontains=section_title)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"categories": serializer.data})

    