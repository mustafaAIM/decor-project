from rest_framework import serializers
from ..models import AreaService

class AreaServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaService
        fields = [
            'uuid', 'title', 'description', 'notes',
            'phone_number', 'email', 'address','city',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'status', 'title'] 