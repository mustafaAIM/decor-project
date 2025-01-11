from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination

from complaint.models.complaint_model import Complaint, ComplaintStatus
from complaint.serializers.complaint_serializer import (
    ComplaintListSerializer,
    ComplaintDetailSerializer,
    ComplaintCreateSerializer
)
from django.utils import timezone
from complaint.permissions import IsCustomerAndCreateOnly, IsOwnerOrAdmin, IsAdminUser

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ComplaintViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling all complaint-related operations.
    Uses UUID as the lookup field instead of ID.
    """
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'  
    lookup_url_kwarg = 'uuid'  
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'description', 'reference_number']
    ordering_fields = ['created_at', 'updated_at', 'priority', 'status']
    ordering = ['-created_at']
    filterset_fields = {
        'status': ['exact'],
        'priority': ['exact'],
        'created_at': ['gte', 'lte'],
    }

    def get_queryset(self):
        """
        Filter complaints based on user role:
        - Staff users see all complaints
        - Regular users see only their complaints
        """
        queryset = Complaint.objects.select_related('customer')
        if not self.request.user.is_staff:
            queryset = queryset.filter(customer=self.request.user.customer)
        return queryset
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            permission_classes = [IsAuthenticated, IsCustomerAndCreateOnly]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action in ['resolve', 'close', 'reopen']:
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:  
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        return [permission() for permission in permission_classes]


    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ComplaintListSerializer
        elif self.action == 'create':
            return ComplaintCreateSerializer
        return ComplaintDetailSerializer

    def perform_create(self, serializer):
        """Associate the complaint with the current user's customer"""
        serializer.save(customer=self.request.user.customer)

    @action(detail=True, methods=['post'])
    def resolve(self, request, uuid=None):
        """
        Endpoint to mark a complaint as resolved
        POST /api/complaints/{uuid}/resolve/
        """
        complaint = self.get_object()
        if complaint.status == ComplaintStatus.CLOSED:
            return Response(
                {"detail": "Cannot resolve a closed complaint"},
                status=status.HTTP_400_BAD_REQUEST
            )

        complaint.status = ComplaintStatus.RESOLVED
        complaint.resolved_at = timezone.now()
        complaint.save()

        serializer = self.get_serializer(complaint)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def close(self, request, uuid=None):
        """
        Endpoint to close a complaint
        POST /api/complaints/{uuid}/close/
        """
        complaint = self.get_object()
        complaint.status = ComplaintStatus.CLOSED
        complaint.save()

        serializer = self.get_serializer(complaint)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reopen(self, request, uuid=None):
        """
        Endpoint to reopen a closed complaint
        POST /api/complaints/{uuid}/reopen/
        """
        complaint = self.get_object()
        if complaint.status != ComplaintStatus.CLOSED:
            return Response(
                {"detail": "Only closed complaints can be reopened"},
                status=status.HTTP_400_BAD_REQUEST
            )

        complaint.status = ComplaintStatus.IN_PROGRESS
        complaint.save()

        serializer = self.get_serializer(complaint)
        return Response(serializer.data)
