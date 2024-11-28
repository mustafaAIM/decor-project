# django
from django_filters.rest_framework import DjangoFilterBackend
# rest
from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination
# models
from ..models.product_model import Product
# seializers
from ..serializers.product_serializer import ProductSerializer
from ..serializers.product_detail_serialzier import ProductDetailSerializer
from ..filters import ProductFilter
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().select_related('category').prefetch_related('product_colors')
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name']
    ordering = ['name']
    lookup_field = 'uuid'

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'create':
            return ProductSerializer
        return ProductDetailSerializer