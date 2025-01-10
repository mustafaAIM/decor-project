from rest_framework import serializers
from ..models import ServiceOrder
from customer.serializers import CustomerMinimalSerializer
from .area_service_serializer import AreaServiceSerializer
from .consulting_service_serializer import ConsultingServiceSerializer
from .design_service_serializer import DesignServiceSerializer

class ServiceOrderDetailsSerializer(serializers.ModelSerializer):
    customer = CustomerMinimalSerializer(read_only=True)
    service_type = serializers.SerializerMethodField()
    service_details = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceOrder
        fields = [
            'uuid', 'customer', 'service_number', 'service_type',
            'status', 'amount', 'notes', 'created_at', 
            'updated_at', 'completed_at', 'service_details'
        ]
        read_only_fields = fields

    def get_service_type(self, obj):
        return obj.content_type.model
    
    def get_service_details(self, obj):
        service_type = obj.content_type.model
        service = obj.service
        
        if service_type == 'areaservice':
            return AreaServiceSerializer(service).data
        elif service_type == 'consultingservice':
            return ConsultingServiceSerializer(service).data
        elif service_type == 'designservice':
            return DesignServiceSerializer(service).data
        return None 