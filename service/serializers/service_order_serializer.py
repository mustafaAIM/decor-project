from rest_framework import serializers
from ..models import ServiceOrder
from customer.serializers import CustomerMinimalSerializer

class ServiceOrderSerializer(serializers.ModelSerializer):
    customer = CustomerMinimalSerializer(read_only=True)
    service_type = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceOrder
        fields = [
            'uuid', 'customer', 'service_number', 'service_type',
            'status', 'amount', 'notes', 'created_at', 
            'updated_at', 'completed_at'
        ]
        read_only_fields = fields

    def get_service_type(self, obj):
        return obj.content_type.model 