from rest_framework import serializers
from ..models.service_settings_model import ServiceSettings

class ServiceSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceSettings
        fields = ['area_service_cost', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']