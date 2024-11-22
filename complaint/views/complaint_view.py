from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import ValidationError

from complaint.models import Complaint, ComplaintStatus, ComplaintPriority
from complaint.serializers import ComplaintSerializer
from complaint.permissions import IsCustomerOrStaff, CanModifyComplaint
from utils.api_exceptions import BadRequestError, PermissionError, NotFoundError

class ComplaintViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Complaint operations with enhanced security and functionality.
    """
    serializer_class = ComplaintSerializer
    
    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        if self.action == 'statistics':
            permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, CanModifyComplaint]
        else:
            permission_classes = [permissions.IsAuthenticated, IsCustomerOrStaff]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filter complaints based on user role:
        - Customers can only see their own complaints
        - Staff can see all complaints
        """
        user = self.request.user
        if user.is_staff:
            return Complaint.objects.all()
        return Complaint.objects.filter(customer=user.customer)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve a complaint and record resolution timestamp."""
        complaint = self.get_object()
        if complaint.status == ComplaintStatus.RESOLVED:
            raise BadRequestError(
                en_message="Complaint is already resolved",
                ar_message="الشكوى تم حلها بالفعل"
            )
        
        try:
            complaint.status = ComplaintStatus.RESOLVED
            complaint.resolved_at = timezone.now()
            complaint.save(update_fields=['status', 'resolved_at'])
            return Response({'status': 'complaint resolved'})
        except ValidationError as e:
            raise BadRequestError(
                en_message="Failed to resolve complaint",
                ar_message="فشل في حل الشكوى",
                extra_data={'details': str(e)}
            )

    @action(detail=True, methods=['post'])
    def reopen(self, request, pk=None):
        """Reopen a resolved or closed complaint."""
        complaint = self.get_object()
        if complaint.status not in [ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED]:
            raise BadRequestError(
                en_message="Only resolved or closed complaints can be reopened",
                ar_message="يمكن إعادة فتح الشكاوى المحلولة أو المغلقة فقط",
                extra_data={'current_status': complaint.status}
            )
        
        try:
            complaint.status = ComplaintStatus.IN_PROGRESS
            complaint.resolved_at = None
            complaint.save(update_fields=['status', 'resolved_at'])
            return Response({'status': 'complaint reopened'})
        except ValidationError as e:
            raise BadRequestError(
                en_message="Failed to reopen complaint",
                ar_message="فشل في إعادة فتح الشكوى",
                extra_data={'details': str(e)}
            )

    @action(detail=True, methods=['post'])
    def escalate(self, request, pk=None):
        """Escalate complaint priority by one level."""
        complaint = self.get_object()
        priority_order = {
            ComplaintPriority.LOW: ComplaintPriority.MEDIUM,
            ComplaintPriority.MEDIUM: ComplaintPriority.HIGH,
            ComplaintPriority.HIGH: ComplaintPriority.URGENT
        }
        
        if complaint.priority not in priority_order:
            raise BadRequestError(
                en_message="Cannot escalate from current priority level",
                ar_message="لا يمكن تصعيد مستوى الأولوية الحالي",
                extra_data={'current_priority': complaint.priority}
            )
            
        try:
            complaint.priority = priority_order[complaint.priority]
            complaint.save(update_fields=['priority'])
            return Response({'status': 'priority escalated'})
        except ValidationError as e:
            raise BadRequestError(
                en_message="Failed to escalate priority",
                ar_message="فشل في تصعيد الأولوية",
                extra_data={'details': str(e)}
            )

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update complaint status with validation."""
        complaint = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status or new_status not in ComplaintStatus.values:
            raise BadRequestError(
                en_message="Invalid status provided",
                ar_message="الحالة المقدمة غير صالحة",
                extra_data={'valid_statuses': ComplaintStatus.values}
            )

        invalid_transitions = {
            ComplaintStatus.CLOSED: [ComplaintStatus.PENDING, ComplaintStatus.IN_PROGRESS],
            ComplaintStatus.PENDING: [ComplaintStatus.CLOSED],
        }
        
        if (complaint.status in invalid_transitions and 
            new_status in invalid_transitions[complaint.status]):
            raise BadRequestError(
                en_message="Invalid status transition",
                ar_message="انتقال الحالة غير صالح",
                extra_data={
                    'current_status': complaint.status,
                    'requested_status': new_status,
                    'allowed_transitions': [
                        status for status in ComplaintStatus.values 
                        if status not in invalid_transitions.get(complaint.status, [])
                    ]
                }
            )

        try:
            complaint.status = new_status
            if new_status == ComplaintStatus.RESOLVED:
                complaint.resolved_at = timezone.now()
            complaint.save(update_fields=['status', 'resolved_at'])
            return Response({'status': 'status updated successfully'})
        except ValidationError as e:
            raise BadRequestError(
                en_message="Failed to update status",
                ar_message="فشل في تحديث الحالة",
                extra_data={'details': str(e)}
            )

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get complaint statistics (staff only)."""
        if not request.user.is_staff:
            raise PermissionError(
                en_message="Only staff members can access statistics",
                ar_message="يمكن للموظفين فقط الوصول إلى الإحصائيات"
            )

        try:
            queryset = self.get_queryset()
            stats = {
                'total': queryset.count(),
                'pending': queryset.filter(status=ComplaintStatus.PENDING).count(),
                'in_progress': queryset.filter(status=ComplaintStatus.IN_PROGRESS).count(),
                'resolved': queryset.filter(status=ComplaintStatus.RESOLVED).count(),
                'urgent': queryset.filter(priority=ComplaintPriority.URGENT).count(),
            }
            return Response(stats)
        except Exception as e:
            raise BadRequestError(
                en_message="Failed to generate statistics",
                ar_message="فشل في إنشاء الإحصائيات",
                extra_data={'details': str(e)}
            )

    def perform_create(self, serializer):
        """Ensure complaint is associated with the current user."""
        if not self.request.user.is_staff:
            serializer.save(customer=self.request.user.customer)
        else:
            serializer.save()