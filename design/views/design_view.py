# django
from django_filters.rest_framework import DjangoFilterBackend
# rest framework
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework import status
# models
from ..models.desgin_model import Design
from ..models.design_file_model import DesignFile
# serializers
from ..serializers.design_serializer import DesignSerializer
from ..serializers.design_update_serializer import DesignUpdateSerializer
from ..serializers.design_file_serialzier import DesignFileSerializer
from ..serializers.add_file_serializer import AddFileSerializer
# utils
from utils.messages import ResponseFormatter
from utils.api_exceptions import BadRequestError, NotFoundError, APIError

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class DesignViewSet(viewsets.ModelViewSet):
    queryset = Design.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ['title']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'uuid']  
    ordering = ['title']  
    lookup_field = 'uuid'

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return DesignUpdateSerializer
        return DesignSerializer

    def list(self, request):
        page = self.paginate_queryset(self.queryset)
        data = []
        for design in page:
            primary_file = design.files.filter(is_primary=True).first()
            data.append({
                'uuid': design.uuid,
                'title': design.title,
                'description': design.description,
                'category': str(design.category.uuid),
                'primary_image': primary_file.file.url if primary_file else None
            })
        return self.get_paginated_response(data)

    def retrieve(self, request, uuid=None):
        design = self.get_object()
        data = {
            'uuid': design.uuid,
            'title': design.title,
            'description': design.description,
            'category': str(design.category.uuid),
            'files': DesignFileSerializer(design.files.all(), many=True).data
        }
        return ResponseFormatter.success_response(data=data)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            return ResponseFormatter.success_response(
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
            
        except serializers.ValidationError as e:
            print(serializer.errors)
            raise BadRequestError(
                en_message="Validation error",
                ar_message="خطأ في التحقق"
            )
            
        except Exception as e:
            raise APIError(
                en_message="An error occurred while creating the design",
                ar_message="حدث خطأ أثناء إنشاء التصميم",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )