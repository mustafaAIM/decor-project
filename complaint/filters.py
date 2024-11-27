import django_filters
from .models import Complaint

class ComplaintFilter(django_filters.FilterSet):
    """Filter set for Complaint model"""
    created_at_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Complaint
        fields = {
            'status': ['exact'],
            'priority': ['exact'],
            'customer': ['exact'],
            'reference_number': ['exact', 'icontains'],
        } 