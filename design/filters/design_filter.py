# core
from django_filters import rest_framework as django_filters
# uuid
import uuid
# models
from section.models.category_model import Category
from ..models.desgin_model import Design
# utile
from utils.api_exceptions import BadRequestError

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

class DesignFilter(django_filters.FilterSet):
    category = UUIDInFilter(field_name='category__uuid')

    class Meta:
        model = Design
        fields = ['category']
