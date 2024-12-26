# rest
from rest_framework import serializers
# models
from ..models.impementaion_service_model import ImplementaionService, ImplementaionServiceFile

class ImplementaionServiceFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImplementaionServiceFile
        fields = ["uuid",'file', 'file_type', 'created_at']
        read_only_fields = [ 'created_at']

class ImplementaionServiceSerializer(serializers.ModelSerializer):
    files = ImplementaionServiceFileSerializer(many=True, read_only=True)
    section = serializers.UUIDField()
    
    class Meta:
        model = ImplementaionService
        fields = [
            'uuid', 'title', 'notes',
            'start_date', 'end_date',
            'section',
            'area',
            'phone_number', 'email', 'address', 'city',
            'files'
        ]