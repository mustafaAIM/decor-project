from rest_framework import serializers
from ..models.consulting_service_model import ConsultingService
from ..models.service_method_model import ServiceMethod
from employee.models import Employee
from employee.serializers.employee_serializer import EmployeeSerializer
from django.utils import timezone
from datetime import datetime, timedelta

class ConsultingServiceSerializer(serializers.ModelSerializer):
    consultant_uuid = serializers.UUIDField(write_only=True)
    consultant_details = EmployeeSerializer(source='consultant', read_only=True)
    method_uuid = serializers.UUIDField(write_only=True)
    method_details = serializers.SerializerMethodField()
    
    class Meta:
        model = ConsultingService
        fields = [
            'uuid', 'title', 'description', 'notes', 'city',
            'consultant_uuid', 'consultant_details',
            'scheduled_date', 'scheduled_time', 'duration',
            'method_uuid', 'method_details', 'phone_number', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'status', 'title']

    def get_method_details(self, obj):
        return {
            'uuid': obj.method.uuid,
            'name': obj.method.name
        }

    def validate_method_uuid(self, value):
        try:
            method = ServiceMethod.objects.get(uuid=value)
            if not method.is_available:
                raise serializers.ValidationError("This service method is not currently available")
            return method
        except ServiceMethod.DoesNotExist:
            raise serializers.ValidationError("Service method not found")

    def validate(self, data):
        scheduled_date = data.get('scheduled_date')
        scheduled_time = data.get('scheduled_time')
        duration = data.get('duration')
        consultant = data.get('consultant_uuid')

        if scheduled_date < timezone.now().date():
            raise serializers.ValidationError("Cannot schedule consultation for past dates")

        if not self._is_consultant_available(consultant, scheduled_date, scheduled_time, duration):
            raise serializers.ValidationError("Consultant is not available at this time")

        return data

    def create(self, validated_data):
        consultant = validated_data.pop('consultant_uuid')
        method = validated_data.pop('method_uuid')
        
        consulting_service = ConsultingService.objects.create(
            consultant=consultant,
            method=method,
            **validated_data
        )
        
        return consulting_service

    def _is_consultant_available(self, consultant, date, time, duration):
        existing_consultations = ConsultingService.objects.filter(
            consultant=consultant,
            scheduled_date=date,
            status__in=['processing']
        )

        requested_start = datetime.combine(date, time)
        requested_end = requested_start + timedelta(minutes=duration)

        for consultation in existing_consultations:
            existing_start = datetime.combine(
                consultation.scheduled_date,
                consultation.scheduled_time
            )
            existing_end = existing_start + timedelta(minutes=consultation.duration)

            if (requested_start < existing_end and requested_end > existing_start):
                return False

        return True

    def validate_consultant_uuid(self, value):
        try:
            return Employee.objects.get(uuid=value, is_consultable=True)
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Consultant not found or not available for consultation")
