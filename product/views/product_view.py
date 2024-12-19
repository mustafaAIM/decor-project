# django
from django_filters.rest_framework import DjangoFilterBackend
# rest
from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination
# models
from ..models.product_model import Product
# seializers
from ..serializers.product_serializer import ProductSerializer
from ..serializers.product_create_serializer import ProductCreateSerializer
from ..serializers.product_update_serializer import ProductUpdateSerializer
from ..serializers.product_retrive_serialzier import ProductRetrieveSerializer
from ..filters import ProductFilter
# utile
from utils.messages import ResponseFormatter
from utils.shortcuts import get_object_or_404
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
        if self.action == 'list':
            return ProductSerializer
        elif self.action == 'create':
            return ProductCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProductUpdateSerializer
        return ProductRetrieveSerializer

    def retrieve(self, request, uuid=None):
        product = get_object_or_404(Product, uuid=uuid)
        product_design = ProductRetrieveSerializer(product)
        return ResponseFormatter.success_response(data=product_design.data)
    
    def update(self, request, uuid=None, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = get_object_or_404(Product, uuid=uuid)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return ResponseFormatter.success_response(data=serializer.data) 