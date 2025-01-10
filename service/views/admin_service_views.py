from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from ..models import ServiceOrder
from ..serializers.service_order_details_serializer import ServiceOrderDetailsSerializer

class AdminServiceOrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ServiceOrderDetailsSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'uuid'
    
    def get_queryset(self):
        queryset = ServiceOrder.objects.exclude(
            status='PENDING'
        ).select_related(
            'customer',
            'content_type'
        ).order_by('-created_at')
        
        # Filter by status
        status = self.request.query_params.get('status', None)
        if status:
            status = status.upper()
            valid_statuses = ['PROCESSING', 'COMPLETED', 'REFUNDED']
            if status in valid_statuses:
                queryset = queryset.filter(status=status)
            elif status == 'ALL':
                pass
        
        # Filter by service type
        service_type = self.request.query_params.get('type', None)
        if service_type:
            service_type = service_type.lower()
            valid_types = {
                'area': 'areaservice',
                'consulting': 'consultingservice',
                'design': 'designservice',
                'supervision': 'supervisionservice',
                'implementation': 'implementationservice'
            }
            
            if service_type in valid_types:
                content_type = ContentType.objects.get(model=valid_types[service_type])
                queryset = queryset.filter(content_type=content_type)
        
        return queryset 