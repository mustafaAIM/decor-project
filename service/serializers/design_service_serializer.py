from rest_framework import serializers
from ..models import DesignService, DesignServiceFile
from section.serializers import SectionSerializer
from plan.serializers import PlanSerializer
from product.serializers import ColorSerializer

class DesignServiceFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignServiceFile
        fields = ["uuid",'file', 'file_type', 'created_at']
        read_only_fields = [ 'created_at']

class DesignServiceSerializer(serializers.ModelSerializer):
    section_details = SectionSerializer(source='section', read_only=True)
    plan_details = PlanSerializer(source='plan', read_only=True)
    prefered_colors_details = ColorSerializer(source='prefered_colors', many=True, read_only=True)
    files = DesignServiceFileSerializer(many=True, read_only=True)
    
    class Meta:
        model = DesignService
        fields = [
            'uuid', 'title', 'description', 'notes',
            'section', 'section_details',
            'area', 'plan', 'plan_details',
            'prefered_colors', 'prefered_colors_details',
            'phone_number', 'email', 'address',
            'status', 'created_at', 'updated_at',
            'files'
        ]
        read_only_fields = [ 'created_at', 'updated_at', 'status']

    def validate_plan(self, plan):
        if not plan.is_active:
            raise serializers.ValidationError("This plan is not currently active")
        return plan
