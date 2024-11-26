# rest framework
from rest_framework import serializers
# models
from ..models.desgin_model import Design
from ..models.design_file_model import DesignFile
from section.models.category_model import Category
# serializers
from ..serializers.design_file_serialzier import DesignFileSerializer
import json

class DesignSerializer(serializers.ModelSerializer):
    files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=True
    )
    files_data = DesignFileSerializer(many=True, read_only=True, source='files')
    category = serializers.UUIDField()

    class Meta:
        model = Design
        fields = ['uuid', 'title', 'description', 'category', 'files', 'files_data']

    def create(self, validated_data):
        files = validated_data.pop('files', [])
        if not files:
            raise serializers.ValidationError({"files": "This field is required."})

        category_uuid = validated_data.pop('category') 
        category = Category.objects.get(uuid=category_uuid)
        design = Design.objects.create(category=category, **validated_data)

        # Process each file
        has_primary = False
        for index, file in enumerate(files):
            # Create temporary file instance to get file type
            temp_file = DesignFile(file=file)
            file_type = temp_file.get_file_type_from_extension()
            
            if file_type == 'unknown':
                raise serializers.ValidationError({
                    "files": f"File extension not supported for file: {file.name}"
                })

            # Get additional data from request
            request = self.context['request']
            title = request.data.get(f'titles[{index}]', '')
            is_primary = request.data.get(f'is_primary[{index}]', '').lower() == 'true'

            if is_primary and has_primary:
                raise serializers.ValidationError({
                    "files": "Only one file can be primary"
                })
            elif is_primary:
                has_primary = True
            elif index == 0 and not has_primary:
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
        request = self.context['request']
        if request.method == 'POST':
            files_data = request.data.getlist('files', [])
            if not files_data:
                raise serializers.ValidationError({"files": "This field is required."})
            
            primary_count = 0
            for file_data in files_data:
                if not isinstance(file_data, dict):
                    try:
                        file_data = json.loads(file_data)
                    except:
                        raise serializers.ValidationError({
                            "files": "Invalid file data format"
                        })
                
                if file_data.get('is_primary'):
                    primary_count += 1

            if primary_count > 1:
                raise serializers.ValidationError({
                    "files": "Only one file can be primary"
                })

        return data