# rest
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
# django
from django.db import transaction
# models
from ..models.impementaion_service_model import ImplementaionService, ImplementaionServiceFile
from section.models.section_model import Section
# serialziers
from ..serializers.implementaion_service_serializer import ImplementaionServiceSerializer, ImplementaionServiceFileSerializer
# permissions
# utils
from utils import BadRequestError, PermissionError
from utils.messages import ResponseFormatter
from utils.shortcuts import get_object_or_404
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
class ImplementaionServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ImplementaionServiceSerializer
    permission_classes = []
    pagination_class = StandardResultsSetPagination
    parser_classes = (MultiPartParser, FormParser)
    lookup_field = 'uuid'

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.customer:
            return ImplementaionService.objects.filter(customer=self.request.user.customer)
        else:
            return ImplementaionService.objects.all()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        if (not self.request.user.is_authenticated) or (not self.request.user.customer):
            raise PermissionError(en_message='You do not have permission to perform this action.', ar_message='ليس لديك الصلاحيات للقيام بعملية الإنشاء هذه.')

        area_files = request.FILES.getlist('area_file', [])
        design_files = request.FILES.getlist('design_file', [])
        inspiration_files = request.FILES.getlist('inspiration_files', [])
        if request.data.get('section'):
            section_uuid = request.data.get('section')
        else:
            raise BadRequestError(
                en_message="Must specify a section",
                ar_message="يجب تحديد قسم."
            )
        
        if not area_files:
            raise BadRequestError(
                en_message="At least one area file is required",
                ar_message="مطلوب ملف واحد على الأقل للمساحة"
            )
        
        if not design_files:
            raise BadRequestError(
                en_message="At least one design file is required",
                ar_message="مطلوب ملف واحد على الأقل للتصميم"
            )
        
        section = get_object_or_404(Section, uuid=section_uuid)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        implementaion_service = serializer.save(customer=request.user.customer, section=section)

        for file in area_files:
            ImplementaionServiceFile.objects.create(
                service=implementaion_service,
                file=file,
                file_type='area_file'
            )

        for file in design_files:
            ImplementaionServiceFile.objects.create(
                service=implementaion_service,
                file=file,
                file_type='design_file'
            )

        for file in inspiration_files:
            ImplementaionServiceFile.objects.create(
                service=implementaion_service,
                file=file,
                file_type='inspiration'
            )
        
        return ResponseFormatter.success_response(data=serializer.data, status_code=201)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if (not request.user.is_authenticated) or (not hasattr(request.user, 'customer')) or (instance.customer != request.user.customer):
            raise PermissionError(en_message='You do not have permission to perform this action.', ar_message='ليس لديك الصلاحيات للقيام بهذه العملية.')
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if (not request.user.is_authenticated) or (not hasattr(request.user, 'customer')) or (instance.customer != request.user.customer):
            raise PermissionError(en_message='You do not have permission to perform this action.', ar_message='ليس لديك الصلاحيات للقيام بهذه العملية.')
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'], url_path='add-file')
    def add_files(self, request, uuid=None):
        instance = self.get_object()
        if (not request.user.is_authenticated) or (not hasattr(request.user, 'customer')) or (instance.customer != request.user.customer):
            raise PermissionError(en_message='You do not have permission to perform this action.', ar_message='ليس لديك الصلاحيات للقيام بهذه العملية.')
        design_service = self.get_object()
        files = request.FILES.getlist('files', [])
        file_type = request.data.get('file_type')

        if not file_type:
            raise BadRequestError(
                en_message="file type is required",
                ar_message="يجب أن تحدد نوع ملف."
            )

        if not file_type in ['area_file', 'design_file', 'inspiration']:
            raise BadRequestError(
                en_message="Invalid file type",
                ar_message="نوع الملف غير صالح"
            )

        if not files:
            raise BadRequestError(
                en_message="At least one file is required",
                ar_message="مطلوب ملف واحد على الأقل"
            )
        
        created_files = []
        for file in files:
            service_file = ImplementaionServiceFile.objects.create(
                service=design_service,
                file=file,
                file_type=file_type
            )
            created_files.append(service_file)

        serializer = ImplementaionServiceFileSerializer(created_files, many=True)

        return ResponseFormatter.success_response(data=serializer.data, status_code=201)

    @action(detail=True, methods=['delete'], url_path='delete-file')
    def remove_file(self, request, uuid=None):
        instance = self.get_object()
        if (not request.user.is_authenticated) or (not hasattr(request.user, 'customer')) or (instance.customer != request.user.customer):
            raise PermissionError(en_message='You do not have permission to perform this action.', ar_message='ليس لديك الصلاحيات للقيام بهذه العملية.')
        implementation_service = self.get_object()
        file_uuid = request.data.get('file_uuid')

        try:
            file = ImplementaionServiceFile.objects.get(
                uuid=file_uuid,
                service=implementation_service
            )
            file.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        except ImplementaionServiceFile.DoesNotExist:
            raise BadRequestError(
                en_message="File not found",
                ar_message="الملف غير موجود"
            )