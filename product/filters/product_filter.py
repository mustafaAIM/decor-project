# filters
from django_filters import rest_framework as django_filters
from django.core.exceptions import ValidationError
import uuid
from utils.api_exceptions import BadRequestError

# models
from product.models.product_model import Product
from section.models import Category

class UUIDInFilter(django_filters.UUIDFilter):
    def filter(self, qs, value):
        if value:
            try:
                uuid.UUID(str(value))
                if not Category.objects.filter(uuid=value).exists():
                    raise BadRequestError(
                        en_message="Category not found.",
                        ar_message="الفئة غير موجودة"
                    )
            except (ValueError, AttributeError):
                raise BadRequestError(
                    en_message="Invalid UUID format.",
                    ar_message="تنسيق UUID غير صالح"
                )
        return super().filter(qs, value)

class ProductFilter(django_filters.FilterSet):
    category = UUIDInFilter(field_name='category__uuid')
    # category_title = django_filters.CharFilter(field_name='category__title', lookup_expr='icontains')
    # min_price = django_filters.NumberFilter(field_name='product_colors__price', lookup_expr='gte')
    # max_price = django_filters.NumberFilter(field_name='product_colors__price', lookup_expr='lte')
    
    class Meta:
        model = Product
        fields = ['category']
