from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import  AllowAny
from admin.permissions import IsAdmin
from ..models import Plan
from ..serializers.plan_serializer import PlanSerializer
from utils import BadRequestError

class PlanViewSet(viewsets.ModelViewSet):
    serializer_class = PlanSerializer
    lookup_field = 'uuid'
    
    def get_permissions(self):
        """
        Only admin can create/update/delete plans
        Anyone can list/retrieve plans
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdmin]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = Plan.objects.all()
        if self.action == 'list':
            if not self.request.user.is_staff:
                queryset = queryset.filter(is_active=True)
        return queryset

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def toggle_active(self, request, uuid=None):
        plan = self.get_object()
        plan.is_active = not plan.is_active
        plan.save()
        
        return Response({
            'status': 'success',
            'is_active': plan.is_active
        })

    def destroy(self, request, *args, **kwargs):
        plan = self.get_object()
        if plan.designservice_set.exists():
            raise BadRequestError(
                en_message="Cannot delete plan that is being used by design services",
                ar_message="لا يمكن حذف الخطة المستخدمة في خدمات التصميم"
            )
        return super().destroy(request, *args, **kwargs) 