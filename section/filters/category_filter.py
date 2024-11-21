from django_filters import rest_framework as filters
from section.models import Category

class CategoryFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr='icontains')
    section_name = filters.CharFilter(
        field_name='section__name',
        lookup_expr='icontains',
        label='Section Name'
    )

    class Meta:
        model = Category
        fields = ['title', 'section_name']