from rest_framework import viewsets
from admin.permissions import IsAdmin
from ..models.service_settings_model import ServiceSettings
from ..serializers.service_settings_serializer import ServiceSettingsSerializer

class ServiceSettingsViewSet(viewsets.ModelViewSet):
    queryset = ServiceSettings.objects.all()
    serializer_class = ServiceSettingsSerializer
    permission_classes = [IsAdmin]
    
    def get_object(self):
        return ServiceSettings.get_settings()