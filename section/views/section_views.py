#rest
from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
#filter
from django_filters.rest_framework import DjangoFilterBackend
#models
from section.models import Section
#serializers
from section.serializers import SectionSerializer

#permission
from admin.permissions import IsAdminOrReadOnly


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 100

class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [IsAdminOrReadOnly]  
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['title']  
    search_fields = ['title', 'description']  
    ordering_fields = ['title', 'uuid']  
    ordering = ['title']  
    lookup_field = 'uuid'