from rest_framework import serializers
from order.models import Order
from service.models import ServiceOrder
from order.serializers.order_serializers import OrderSerializer
from service.serializers.service_order_serializer import ServiceOrderSerializer
from service.serializers.design_service_serializer import DesignServiceSerializer
from service.serializers.area_service_serializer import AreaServiceSerializer
from service.serializers.consulting_service_serializer import ConsultingServiceSerializer

class CombinedOrderSerializer(serializers.Serializer):
    type = serializers.CharField()
    data = serializers.SerializerMethodField()
    service_details = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()

    def get_data(self, obj):
        if isinstance(obj['data'], Order):
            return OrderSerializer(obj['data']).data
        elif isinstance(obj['data'], ServiceOrder):
            return ServiceOrderSerializer(obj['data']).data
        return None

    def get_service_details(self, obj):
        if isinstance(obj['data'], Order):
            return None
        
        service_order = obj['data']
        service = service_order.service  
        if not service:
            return None

        if obj['type'] == 'service_order_designservice':
            return DesignServiceSerializer(service).data
        elif obj['type'] == 'service_order_areaservice':
            return AreaServiceSerializer(service).data
        elif obj['type'] == 'service_order_consultingservice':
            return ConsultingServiceSerializer(service).data
        
        return None 