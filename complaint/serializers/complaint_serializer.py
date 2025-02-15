from rest_framework import serializers
from complaint.models.complaint_model import Complaint, ComplaintStatus
from customer.serializers import CustomerMinimalSerializer
from django.utils import timezone

class ComplaintBaseSerializer(serializers.ModelSerializer):
    """Base serializer with common fields"""
    uuid = serializers.UUIDField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    customer = CustomerMinimalSerializer(read_only=True)

class ComplaintListSerializer(ComplaintBaseSerializer):
    """Serializer for listing complaints"""
    class Meta:
        model = Complaint
        fields = [
            'id', 'uuid', 'reference_number', 'title', 'status', 
            'status_display', 'priority', 'priority_display', 
            'customer', 'created_at',"description"
        ]
        read_only_fields = ['id', 'uuid', 'reference_number', 'created_at']

class ComplaintDetailSerializer(ComplaintBaseSerializer):
    """Serializer for detailed complaint view and updates"""
    class Meta:
        model = Complaint
        fields = [
            'id', 'uuid', 'reference_number', 'title', 'description',
            'status', 'status_display', 'priority', 'priority_display',
            'customer', 'created_at', 'updated_at', 'resolved_at'
        ]
        read_only_fields = ['id', 'uuid', 'reference_number', 
                           'created_at', 'updated_at', 'resolved_at']

    def validate_status(self, value):
        """Validate status transitions"""
        instance = self.instance
        if instance and instance.status == ComplaintStatus.CLOSED:
            raise serializers.ValidationError("Cannot modify a closed complaint")
        if value == ComplaintStatus.RESOLVED:
            self.context['resolved_now'] = True
        return value

    def update(self, instance, validated_data):
        if self.context.get('resolved_now'):
            validated_data['resolved_at'] = timezone.now()
        return super().update(instance, validated_data)

class ComplaintCreateSerializer(ComplaintBaseSerializer):
    """Serializer for creating new complaints"""
    class Meta:
        model = Complaint
        fields = ['title', 'description', 'priority']
