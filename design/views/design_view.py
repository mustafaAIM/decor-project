# django
from django_filters.rest_framework import DjangoFilterBackend
# rest framework
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from rest_framework.response import Response
from rest_framework import serializers
# models
from ..models.desgin_model import Design
# serializers
from ..serializers.design_serializer import DesignSerializer
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
        designs = self.queryset
        data = []
        for design in designs:
            primary_file = design.files.filter(is_primary=True).first()
            data.append({
                'uuid': design.uuid,
                'title': design.title,
                'primary_image': primary_file.file.url if primary_file else None
            })
        return Response(data)

    def retrieve(self, request, pk=None):
        design = self.get_object()
        serializer = self.get_serializer(design)
        return Response(serializer.data)

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