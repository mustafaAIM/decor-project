# rest framework
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
# models
from ..models.design_file_model import DesignFile
from ..models.desgin_model import Design
# serializers
from ..serializers.add_file_serializer import AddFileSerializer
from ..serializers.design_file_serialzier import DesignFileSerializer
# utile
from utils.api_exceptions import BadRequestError, NotFoundError
from utils.messages import ResponseFormatter

class DesignFileViewSet(viewsets.ViewSet):
    def get_design(self, uuid):
        try:
            return Design.objects.get(uuid=uuid)
        except Design.DoesNotExist:
            raise NotFoundError(
                en_message="Design not found.",
                ar_message="التصميم غير موجود."
            )

    @action(detail=False, methods=['post'], url_path='add-file')
    def add_file(self, request):
        design_uuid = request.data.get('design')
        if not design_uuid:
            raise BadRequestError(
                en_message="Design UUID is required.",
                ar_message="معرف التصميم مطلوب."
            )

        design = self.get_design(design_uuid)
        serializer = AddFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data['file']
        title = serializer.validated_data['title']
        is_primary = serializer.validated_data['is_primary']

        if is_primary and design.files.filter(is_primary=True).exists():
            raise BadRequestError(
                en_message="Only one file can be primary.",
                ar_message="يمكن أن يكون ملف واحد فقط أساسيًا."
            )

        temp_file = DesignFile(file=file)
        file_type = temp_file.get_file_type_from_extension()

        if file_type == 'unknown':
            raise BadRequestError(
                en_message="File extension not supported.",
                ar_message="امتداد الملف غير مدعوم."
            )

        DesignFile.objects.create(
            design=design,
            file=file,
            file_type=file_type,
            is_primary=is_primary,
            title=title
        )

        return ResponseFormatter.success_response(
            data={"message": "File added successfully."},
            status_code=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['delete'], url_path='delete-file')
    def delete_file(self, request):
        design_uuid = request.data.get('design')
        file_uuid = request.data.get('file')
        
        if not design_uuid or not file_uuid:
            raise BadRequestError(
                en_message="Design UUID and File UUID are required.",
                ar_message="معرف التصميم ومعرف الملف مطلوبان."
            )

        design = self.get_design(design_uuid)
        try:
            file = design.files.get(uuid=file_uuid)
            file.delete()
            return ResponseFormatter.success_response(
                data={"message": "File deleted successfully."},
                status_code=status.HTTP_204_NO_CONTENT
            )
        except DesignFile.DoesNotExist:
            raise NotFoundError(
                en_message="File not found.",
                ar_message="الملف غير موجود."
            )