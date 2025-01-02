# filters
from django_filters import rest_framework as django_filters
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
    section = django_filters.UUIDFilter(field_name='category__section__uuid')
    
    class Meta:
        model = Product
        fields = ['category', 'section']
