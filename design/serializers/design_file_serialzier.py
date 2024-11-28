# rest framework
from rest_framework import serializers
# models
from ..models.design_file_model import DesignFile

class DesignFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignFile
        fields = ['uuid', 'file', 'file_type', 'is_primary', 'title']
        read_only_fields = ['file_type']

    def get_file_url(self, obj):
        if obj.file:
            return obj.file.url
        return None