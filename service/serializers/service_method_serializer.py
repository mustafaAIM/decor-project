from rest_framework import serializers
from ..models.service_method_model import ServiceMethod

class ServiceMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceMethod
        fields = ['uuid', 'name', 'is_available', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at'] 