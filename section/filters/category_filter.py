from django_filters import rest_framework as filters
from section.models import Category

class CategoryFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr='icontains')
    section_title = filters.CharFilter(
        field_name='section__title',
        lookup_expr='icontains',
        label='Section Title'
    )

    class Meta:
        model = Category
        fields = ['title', 'section_title']