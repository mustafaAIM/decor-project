from rest_framework import serializers
from ..models.employee_model import Employee, Department, WorkingHours
from authentication.serializers.user_serializers import UserProfileSerializer
from authentication.models import User
from utils import BadRequestError

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['uuid', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['uuid', 'created_at', 'updated_at']

class WorkingHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingHours
        fields = ['day', 'from_hour', 'to_hour']

class EmployeeUserSerializer(UserProfileSerializer):
    email = serializers.EmailField(required=True)
    
    class Meta(UserProfileSerializer.Meta):
        model = User
        fields = UserProfileSerializer.Meta.fields + ('email',)
        read_only_fields = ('uuid',)

    def update(self, instance, validated_data):
        email = validated_data.pop('email', None)
        
        # Update user fields using parent serializer
        instance = super().update(instance, validated_data)
        
        # Update email separately if provided
        if email is not None:
            instance.email = email
            instance.save()
            
        return instance

class EmployeeSerializer(serializers.ModelSerializer):
    user = EmployeeUserSerializer()
    working_hours = WorkingHoursSerializer(many=True, required=False)
    department = DepartmentSerializer(read_only=True)
    department_uuid = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = Employee
        fields = ['uuid', 'user', 'salary', 'department', 'department_uuid', 
                 'is_consultable', 'working_hours', 'created_at', 'updated_at']
        read_only_fields = ['uuid', 'created_at', 'updated_at']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        working_hours_data = validated_data.pop('working_hours', [])
        department_uuid = validated_data.pop('department_uuid', None)

        user_serializer = EmployeeUserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        if department_uuid:
            department = Department.objects.get(uuid=department_uuid)
            validated_data['department'] = department

        employee = Employee.objects.create(user=user, **validated_data)

        for hours_data in working_hours_data:
            WorkingHours.objects.create(employee=employee, **hours_data)

        return employee

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        working_hours_data = validated_data.pop('working_hours', None)
        department_uuid = validated_data.pop('department_uuid', None)

        if user_data:
            user_serializer = EmployeeUserSerializer(
                instance.user,
                data=user_data,
                partial=True
            )
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        if department_uuid:
            department = Department.objects.get(uuid=department_uuid)
            instance.department = department

        if working_hours_data is not None:
            instance.working_hours.all().delete()
            for hours_data in working_hours_data:
                WorkingHours.objects.create(employee=instance, **hours_data)

        return super().update(instance, validated_data) 