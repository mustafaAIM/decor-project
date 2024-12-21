# django
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Min, Max
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
from ..utils.search import AdvancedSearchFilter
from utils.messages import ResponseFormatter
from utils.shortcuts import get_object_or_404
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().select_related('category').prefetch_related(
        'product_colors', 'ratings'
    )
    pagination_class = StandardResultsSetPagination
    filter_backends = (
        DjangoFilterBackend, 
        AdvancedSearchFilter,
        filters.OrderingFilter
    )
    filterset_class = ProductFilter
    search_fields = [
        'name', 
        'description', 
        'category__title',
        'product_colors__color__hex_code'
    ]
    ordering_fields = [
        'name',
        'created_at',
        'average_rating',
        'price_min',
        'price_max'
    ]
    ordering = ['name']
    lookup_field = 'uuid'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Annotate with price ranges
        queryset = queryset.annotate(
            price_min=Min('product_colors__price'),
            price_max=Max('product_colors__price')
        )

        # Apply price range filter
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price_min__gte=min_price)
        if max_price:
            queryset = queryset.filter(price_max__lte=max_price)

        # Apply color filter
        color = self.request.query_params.get('color')
        if color:
            queryset = queryset.filter(product_colors__color__hex_code=color)

        # Apply availability filter
        in_stock = self.request.query_params.get('in_stock')
        if in_stock:
            queryset = queryset.filter(product_colors__quantity__gt=0)

        return queryset.distinct()

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
        serialized_product = ProductRetrieveSerializer(product)
        product = serialized_product.data
        for product_color in product['product_colors']:
            product_color['image'] = request.build_absolute_uri(product_color['image']) if product_color['image'] else None
        return ResponseFormatter.success_response(data=product)
    
    def update(self, request, uuid=None, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = get_object_or_404(Product, uuid=uuid)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return ResponseFormatter.success_response(data=serializer.data) 