# rest framework
from rest_framework import serializers
# models
from ..models.desgin_model import Design
from section.models.category_model import Category
# serializers
from ..serializers.design_file_serialzier import DesignFileSerializer
# utile
from utils.shortcuts import get_object_or_404
from utils.api_exceptions import BadRequestError

class DesignSerializer(serializers.ModelSerializer):
    files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=True
    )
    titles = serializers.ListField(
        child=serializers.CharField(max_length=255),
        write_only=True,
        required=True
    )
    is_primary = serializers.ListField(
        child=serializers.BooleanField(),
        write_only=True,
        required=True
    )
    files_data = DesignFileSerializer(many=True, read_only=True, source='files')
    category = serializers.UUIDField()

    class Meta:
        model = Design
        fields = ['uuid', 'title', 'description', 'category', 'files', 'titles', 'is_primary', 'files_data']

    def validate(self, data):
        files = data.get('files', [])
        titles = data.get('titles', [])
        is_primary_list = data.get('is_primary', [])
        if not files:
            raise BadRequestError(
                en_message="At least one file is required.",
                ar_message="مطلوب ملف واحد على الأقل."
            )

        if len(files) != len(titles) or len(files) != len(is_primary_list):
            raise BadRequestError(
                en_message="Files, titles, and is_primary lists must have the same length.",
                ar_message="يجب أن تكون قوائم الملفات والعناوين والحقول الأساسية بنفس الطول."
            )

        if not any(is_primary_list):
            raise BadRequestError(
                en_message="At least one file must be marked as primary.",
                ar_message="يجب تحديد ملف واحد على الأقل كملف أساسي."
            )

        if sum(1 for x in is_primary_list if x) > 1:
            raise BadRequestError(
                en_message="Only one file can be marked as primary.",
                ar_message="يمكن تحديد ملف واحد فقط كملف أساسي."
            )
        
        category_uuid = data.pop('category', None) 
        if not category_uuid:
            raise BadRequestError(
                en_message="Should specify a category for the design",
                ar_message="يجب تحديد تصنيف للتصميم."
            )
        category = get_object_or_404(Category, uuid=category_uuid)

        return data