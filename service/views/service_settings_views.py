from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from admin.permissions import IsAdmin
from ..models.service_settings_model import ServiceSettings
from ..serializers.service_settings_serializer import ServiceSettingsSerializer

class ServiceSettingsPermission(IsAuthenticated):
    def has_permission(self, request, view):
        # Check if user is authenticated first
        if not super().has_permission(request, view):
            return False
            
        # Allow read operations for all authenticated users
        if request.method in SAFE_METHODS:
            return True
            
        # Require admin permissions for write operations
        return IsAdmin().has_permission(request, view)

class ServiceSettingsViewSet(viewsets.ModelViewSet):
    queryset = ServiceSettings.objects.all()
    serializer_class = ServiceSettingsSerializer
    permission_classes = [ServiceSettingsPermission]
    
    def get_object(self):
        return ServiceSettings.get_settings()
    
    def create(self, request, *args, **kwargs):
        settings = ServiceSettings.objects.first()
        
        if settings:
            serializer = self.get_serializer(settings, data=request.data)
        else:
            serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def list(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)