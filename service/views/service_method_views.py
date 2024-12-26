from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models.service_method_model import ServiceMethod
from ..serializers.service_method_serializer import ServiceMethodSerializer
from admin.permissions import IsAdmin
from rest_framework.permissions import IsAuthenticated

class ServiceMethodViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceMethodSerializer
    lookup_field = 'uuid'
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'available']:
            return [IsAuthenticated()]
        return [IsAdmin()]

    def get_queryset(self):
        return ServiceMethod.objects.all()

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get only available service methods"""
        methods = ServiceMethod.objects.filter(is_available=True)
        serializer = self.get_serializer(methods, many=True)
        return Response(serializer.data) 