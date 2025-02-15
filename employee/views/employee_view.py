from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from ..models.employee_model import Employee, Department
from ..serializers.employee_serializer import EmployeeSerializer, DepartmentSerializer
from django.shortcuts import get_object_or_404
from admin.permissions import IsAdmin
from utils import ResponseFormatter, BadRequestError
from django.db.models import Q
from authentication.models import User

class DepartmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = DepartmentSerializer
    lookup_field = 'uuid'

    def get_queryset(self):
        return Department.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"data": serializer.data})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"data": serializer.data})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"data": serializer.data})

class EmployeeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeSerializer
    lookup_field = 'uuid'

    def get_queryset(self):
        queryset = Employee.objects.all()
        is_consultable = self.request.query_params.get('is_consultable', None)
        if is_consultable is not None:
            is_consultable = is_consultable.lower() == 'true'
            queryset = queryset.filter(is_consultable=is_consultable)
        return queryset.select_related('user', 'department').prefetch_related('working_hours')

    def get_object(self):
        return get_object_or_404(Employee, uuid=self.kwargs['uuid'])

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"data": serializer.data})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"data": serializer.data})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if 'user' in request.data and 'email' in request.data['user']:
            email = request.data['user']['email']
            if User.objects.filter(
                ~Q(id=instance.user.id),  
                email=email
            ).exists():
                print(instance.user.first_name , instance.user.id , instance.user.email)
                raise BadRequestError(
                    en_message="Email is already registered.",
                    ar_message="البريد الإلكتروني مسجل بالفعل."
                )
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"data": serializer.data})

    @action(detail=False, methods=['get'])
    def consultants(self, request):
        """
        Get all consultable employees
        """
        consultants = self.get_queryset().filter(is_consultable=True)
        serializer = self.get_serializer(consultants, many=True)
        return ResponseFormatter.success_response(data=serializer.data) 