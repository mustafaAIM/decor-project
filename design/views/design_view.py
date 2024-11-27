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
from ..serializers.design_file_serialzier import DesignFileSerializer
from ..serializers.add_file_serializer import AddFileSerializer
# utils
from utils.messages import ResponseFormatter

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class DesignViewSet(viewsets.ModelViewSet):
    queryset = Design.objects.all()
    serializer_class = DesignSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ['title']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'uuid']  
    ordering = ['title']  
    lookup_field = 'uuid'

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
        return Response(data)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            return ResponseFormatter.success_response(
                en="Design created successfully",
                ar="تم إنشاء التصميم بنجاح",
                status=201,
                data=serializer.data
            )
            
        except serializers.ValidationError as e:
            print(request)
            print(request.data)
            return Response(
                {
                    "message": {
                        "status": "400",
                        "en": "Validation error",
                        "ar": "خطأ في التحقق"
                    },
                    "errors": e.detail
                },
                status=400
            )
            
        except Exception as e:
            return Response(
                {
                    "message": {
                        "status": "500",
                        "en": "An error occurred while creating the design",
                        "ar": "حدث خطأ أثناء إنشاء التصميم"
                    },
                    "errors": {"detail": str(e)}
                },
                status=500
            )

    @action(detail=True, methods=['post'], url_path='add-file')
    def add_file(self, request, uuid=None):
        design = self.get_object()
        serializer = AddFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data['file']
        title = serializer.validated_data['title']
        is_primary = serializer.validated_data['is_primary']

        if is_primary and design.files.filter(is_primary=True).exists():
            return Response(
                {"error": "Only one file can be primary."},
                status=status.HTTP_400_BAD_REQUEST
            )

        temp_file = DesignFile(file=file)
        file_type = temp_file.get_file_type_from_extension()

        if file_type == 'unknown':
            return Response(
                {"error": "File extension not supported."},
                status=status.HTTP_400_BAD_REQUEST
            )

        DesignFile.objects.create(
            design=design,
            file=file,
            file_type=file_type,
            is_primary=is_primary,
            title=title
        )

        return Response({"message": "File added successfully."}, status=status.HTTP_201_CREATED)