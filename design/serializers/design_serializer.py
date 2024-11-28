# rest framework
from rest_framework import serializers
# models
from ..models.desgin_model import Design
from ..models.design_file_model import DesignFile
from section.models.category_model import Category
# serializers
from ..serializers.design_file_serialzier import DesignFileSerializer
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
    category = serializers.UUIDField(required=True)

    class Meta:
        model = Design
        fields = ['uuid', 'title', 'description', 'category', 'files', 'titles', 'is_primary', 'files_data']

    def create(self, validated_data):
        files = validated_data.pop('files', [])
        titles = validated_data.pop('titles', [])
        is_primary_list = validated_data.pop('is_primary', [])

        if not files or not titles or not is_primary_list:
            raise BadRequestError(
                en_message="Files, titles, and is_primary fields are required.",
                ar_message="الملفات والعناوين والحقول الأساسية مطلوبة."
            )

        if len(files) != len(titles) or len(files) != len(is_primary_list):
            raise BadRequestError(
                en_message="Files, titles, and is_primary lists must have the same length.",
                ar_message="يجب أن تكون قوائم الملفات والعناوين والحقول الأساسية بنفس الطول."
            )

        category_uuid = validated_data.pop('category') 
        category = Category.objects.get(uuid=category_uuid)
        design = Design.objects.create(category=category, **validated_data)

        # Process each file
        has_primary = False
        for file, title, is_primary in zip(files, titles, is_primary_list):
            temp_file = DesignFile(file=file)
            file_type = temp_file.get_file_type_from_extension()
            
            if file_type == 'unknown':
                raise BadRequestError(
                    en_message=f"File extension not supported for file: {file.name}",
                    ar_message="امتداد الملف غير مدعوم"
                )

            if is_primary and has_primary:
                raise BadRequestError(
                    en_message="Only one file can be primary",
                    ar_message="يمكن أن يكون ملف واحد فقط أساسيًا"
                )
            elif is_primary:
                has_primary = True
            elif not has_primary:
                is_primary = True
                has_primary = True

            DesignFile.objects.create(
                design=design,
                file=file,
                file_type=file_type,
                is_primary=is_primary,
                title=title
            )

        return design

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

        return data