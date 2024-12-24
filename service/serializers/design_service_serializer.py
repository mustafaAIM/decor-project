from rest_framework import serializers
from ..models import DesignService, DesignServiceFile
from section.serializers import SectionSerializer
from plan.serializers import PlanSerializer
from product.serializers import ColorSerializer
from product.models import Color

class DesignServiceFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignServiceFile
        fields = ["uuid",'file', 'file_type', 'created_at']
        read_only_fields = ['created_at']

class DesignServiceSerializer(serializers.ModelSerializer):
    section_details = SectionSerializer(source='section', read_only=True)
    plan_details = PlanSerializer(source='plan', read_only=True)
    prefered_colors = serializers.ListField(
        child=serializers.CharField(max_length=7),
        write_only=True,
        required=False
    )
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
        read_only_fields = ['created_at', 'updated_at', 'status', 'title']

    def validate_prefered_colors(self, value):
        """Validate hex color codes"""
        for hex_color in value:
            if not hex_color.startswith('#'):
                raise serializers.ValidationError(f"Color code {hex_color} must start with #")
            if len(hex_color) != 7:  
                raise serializers.ValidationError(f"Color code {hex_color} must be in #RRGGBB format")
            try:
                int(hex_color[1:], 16)
            except ValueError:
                raise serializers.ValidationError(f"Invalid hex color code: {hex_color}")
        return value

    def validate_plan(self, plan):
        if not plan.is_active:
            raise serializers.ValidationError("This plan is not currently active")
        return plan

    def create(self, validated_data):
        hex_colors = validated_data.pop('prefered_colors', [])
        validated_data['title'] = "Design Service"
        
        instance = super().create(validated_data)
        
        if hex_colors:
            colors = []
            for hex_color in hex_colors:
                color, _ = Color.objects.get_or_create(
                    hex_code=hex_color
                )
                colors.append(color)
            
            instance.prefered_colors.set(colors)
        
        return instance

    def update(self, instance, validated_data):
        hex_colors = validated_data.pop('prefered_colors', None)
        
        instance = super().update(instance, validated_data)
        
        if hex_colors is not None:
            colors = []
            for hex_color in hex_colors:
                color, _ = Color.objects.get_or_create(
                    hex_code=hex_color,
                    defaults={'name': f'Color {hex_color}'}
                )
                colors.append(color)
            
            instance.prefered_colors.set(colors)
        
        return instance
