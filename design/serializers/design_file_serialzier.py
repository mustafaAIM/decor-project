# rest framework
from rest_framework import serializers
# models
from ..models.design_file_model import DesignFile

class DesignFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignFile
        fields = ['id', 'file', 'file_type', 'is_primary', 'title']
        read_only_fields = ['file_type']