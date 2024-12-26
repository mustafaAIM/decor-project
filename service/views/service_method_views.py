from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models.service_method_model import ServiceMethod
from ..serializers.service_method_serializer import ServiceMethodSerializer
from admin.permissions import IsAdmin
from rest_framework.permissions import IsAuthenticated
from utils import ResponseFormatter

class ServiceMethodViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceMethodSerializer
    lookup_field = 'uuid'
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'available']:
            return [IsAuthenticated()]
        return [IsAdmin()]

    def get_queryset(self):
        return ServiceMethod.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return ResponseFormatter.success_response(data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ResponseFormatter.success_response(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return ResponseFormatter.success_response(data=serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return ResponseFormatter.success_response(data=serializer.data)

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get only available service methods"""
        methods = ServiceMethod.objects.filter(is_available=True)
        serializer = self.get_serializer(methods, many=True)
        return ResponseFormatter.success_response(data=serializer.data) 