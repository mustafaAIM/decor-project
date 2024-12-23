from rest_framework import serializers
import os

class FileSerializer(serializers.ModelSerializer):
    file_name = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()

    class Meta:
        abstract = True
        fields = [
            'uuid', 'file', 'file_url', 'file_type',
            'file_name', 'file_size', 'is_primary',
            'title', 'created_at', 'updated_at'
        ]
        read_only_fields = ['file_name', 'file_size', 'created_at', 'updated_at']

    def get_file_name(self, obj):
        return os.path.basename(obj.file.name) if obj.file else None

    def get_file_size(self, obj):
        try:
            return obj.file.size if obj.file else None
        except (FileNotFoundError, ValueError):
            return None

    def get_file_url(self, obj):
        try:
            return obj.file.url if obj.file else None
        except ValueError:
            return None

    def validate_file(self, value):
        ext = value.name.split('.')[-1].lower()
        
        allowed_extensions = {
            'image': ['jpg', 'jpeg', 'png'],
            'pdf': ['pdf'],
            'cad': ['dwg', 'dxf'],
            '3d': ['3ds', 'max']
        }
        
        file_type = self.initial_data.get('file_type')
        
        if file_type and file_type in allowed_extensions:
            if ext not in allowed_extensions[file_type]:
                raise serializers.ValidationError(
                    f"Invalid file extension for {file_type}. "
                    f"Allowed extensions are: {', '.join(allowed_extensions[file_type])}"
                )
        
            
        return value 