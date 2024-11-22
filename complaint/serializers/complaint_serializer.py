from rest_framework import serializers
from complaint.models import Complaint
from customer.serializers import CustomerMinimalSerializer
from django.utils import timezone

class ComplaintListSerializer(serializers.ModelSerializer):
    customer = CustomerMinimalSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Complaint
        fields = ['id', 'reference_number', 'title', 'status', 'status_display', 
                 'priority', 'customer', 'created_at']
        read_only_fields = ['reference_number', 'created_at']

class ComplaintDetailSerializer(serializers.ModelSerializer):
    customer = CustomerMinimalSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Complaint
        fields = '__all__'
        read_only_fields = ['reference_number', 'created_at', 'updated_at', 'resolved_at']

    def validate(self, data):
        """Custom validation for complaint data"""
        if 'status' in data and data['status'] == Complaint.ComplaintStatus.RESOLVED:
            if not data.get('resolved_at'):
                data['resolved_at'] = timezone.now()
        return data