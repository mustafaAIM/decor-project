# django
from django_filters.rest_framework import DjangoFilterBackend
# rest framework
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from rest_framework import serializers
from rest_framework import status
# models
from ..models.desgin_model import Design
# serializers
from ..serializers.design_serializer import DesignSerializer
from ..serializers.design_update_serializer import DesignUpdateSerializer
from ..serializers.design_file_serialzier import DesignFileSerializer
from ..serializers.design_create_serializer import DesignCreateSerializer
# utils
from utils.messages import ResponseFormatter
from utils.api_exceptions import BadRequestError, APIError
from utils.shortcuts import get_object_or_404
from utils.notification import send_notification
# filters
from ..filters.design_filter import DesignFilter

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class DesignViewSet(viewsets.ModelViewSet):
    queryset = Design.objects.all().select_related('category').order_by('title')
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_class = DesignFilter
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'uuid']  
    ordering = ['title'] 
    lookup_field = 'uuid'

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return DesignUpdateSerializer
        if self.action == 'create':
            return DesignCreateSerializer
        return DesignSerializer

    def list(self, request):
        filtered_queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(filtered_queryset)
        data = []
        for design in page:
            primary_file = design.files.filter(is_primary=True).first()
            data.append({
                'uuid': design.uuid,
                'title': design.title,
                'description': design.description,
                'category': design.category.title,
                'primary_image': request.build_absolute_uri(primary_file.file.url) if primary_file else None
            })
        return self.get_paginated_response(data)

    def retrieve(self, request, uuid=None):
        design = get_object_or_404(Design, uuid=uuid)
        files_data = DesignFileSerializer(design.files.all(), many=True).data
        for f in files_data:
            f['file'] = request.build_absolute_uri(f['file'])
        data = {
            'uuid': design.uuid,
            'title': design.title,
            'description': design.description,
            'category': design.category.title,
            'files': files_data
        }
        return ResponseFormatter.success_response(data=data)
    
    def update(self, request, uuid=None, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = get_object_or_404(Design, uuid=uuid)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return ResponseFormatter.success_response(data=serializer.data) 