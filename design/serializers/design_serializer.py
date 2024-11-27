# rest framework
from rest_framework import serializers
# models
from ..models.desgin_model import Design
from ..models.design_file_model import DesignFile
from section.models.category_model import Category
# serializers
from ..serializers.design_file_serialzier import DesignFileSerializer

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

    def create(self, validated_data):
        files = validated_data.pop('files', [])
        titles = validated_data.pop('titles', [])
        is_primary_list = validated_data.pop('is_primary', [])

        if not files or not titles or not is_primary_list:
            raise serializers.ValidationError({"files": "Files, titles, and is_primary fields are required."})

        if len(files) != len(titles) or len(files) != len(is_primary_list):
            raise serializers.ValidationError({"files": "Files, titles, and is_primary lists must have the same length."})

        category_uuid = validated_data.pop('category') 
        category = Category.objects.get(uuid=category_uuid)
        design = Design.objects.create(category=category, **validated_data)

        # Process each file
        has_primary = False
        for file, title, is_primary in zip(files, titles, is_primary_list):
            temp_file = DesignFile(file=file)
            file_type = temp_file.get_file_type_from_extension()
            
            if file_type == 'unknown':
                raise serializers.ValidationError({
                    "files": f"File extension not supported for file: {file.name}"
                })

            if is_primary and has_primary:
                raise serializers.ValidationError({
                    "files": "Only one file can be primary"
                })
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

    def update(self, instance, validated_data):
        files_data = validated_data.pop('files', None)
        category_uuid = validated_data.pop('category', None)
        if category_uuid:
            category = Category.objects.get(uuid=category_uuid)
            instance.category = category
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.category = validated_data.get('category', instance.category)
        instance.save()
        if files_data:
            for file_data in files_data:
                DesignFile.objects.create(design=instance, **file_data)
        return instance

    def validate(self, data):
        files = data.get('files', [])
        titles = data.get('titles', [])
        is_primary_list = data.get('is_primary', [])

        # Check if at least one file is provided
        if not files:
            raise serializers.ValidationError({"files": "At least one file is required."})

        # Check if lists have matching lengths
        if len(files) != len(titles) or len(files) != len(is_primary_list):
            raise serializers.ValidationError({
                "files": "Files, titles, and is_primary lists must have the same length."
            })

        # Check if at least one file is marked as primary
        if not any(is_primary_list):
            raise serializers.ValidationError({
                "is_primary": "At least one file must be marked as primary."
            })

        # Check if multiple files are marked as primary
        if sum(1 for x in is_primary_list if x) > 1:
            raise serializers.ValidationError({
                "is_primary": "Only one file can be marked as primary."
            })

        return data