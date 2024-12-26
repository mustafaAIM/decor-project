from rest_framework import serializers
from ..models.consulting_service_model import ConsultingService
from employee.models import Employee
from employee.serializers.employee_serializer import EmployeeSerializer
from django.utils import timezone
from datetime import datetime, timedelta

class ConsultingServiceSerializer(serializers.ModelSerializer):
    consultant_uuid = serializers.UUIDField(write_only=True)
    consultant_details = EmployeeSerializer(source='consultant', read_only=True)
    
    class Meta:
        model = ConsultingService
        fields = [
            'uuid', 'title', 'description', 'notes',
            'consultant_uuid', 'consultant_details',
            'scheduled_date', 'scheduled_time', 'duration',
            'method', 'phone_number', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'status', 'title']

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
        
        consulting_service = ConsultingService.objects.create(
            consultant=consultant,
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
