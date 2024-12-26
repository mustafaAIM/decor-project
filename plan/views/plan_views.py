from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from admin.permissions import IsAdmin
from ..models import Plan
from ..serializers.plan_serializer import PlanSerializer
from utils import BadRequestError
from authentication.utils import message

class PlanViewSet(viewsets.ModelViewSet):
    serializer_class = PlanSerializer
    lookup_field = 'uuid'
    
    def get_permissions(self):
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

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response_data = {
            **message(
                en="Plans retrieved successfully",
                ar="تم استرجاع الخطط بنجاح",
                status="success"
            ),
            "data": serializer.data
        }
        return Response(response_data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response_data = {
            **message(
                en="Plan retrieved successfully",
                ar="تم استرجاع الخطة بنجاح",
                status="success"
            ),
            "data": serializer.data
        }
        return Response(response_data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        response_data = {
            **message(
                en="Plan created successfully",
                ar="تم إنشاء الخطة بنجاح",
                status="success"
            ),
            "data": serializer.data
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        response_data = {
            **message(
                en="Plan updated successfully",
                ar="تم تحديث الخطة بنجاح",
                status="success"
            ),
            "data": serializer.data
        }
        return Response(response_data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def toggle_active(self, request, uuid=None):
        plan = self.get_object()
        plan.is_active = not plan.is_active
        plan.save()
        
        response_data = {
            **message(
                en="Plan status updated successfully",
                ar="تم تحديث حالة الخطة بنجاح",
                status="success"
            ),
            "data": {"is_active": plan.is_active}
        }
        return Response(response_data)

    def destroy(self, request, *args, **kwargs):
        plan = self.get_object()
        if plan.designservice_set.exists():
            raise BadRequestError(
                en_message="Cannot delete plan that is being used by design services",
                ar_message="لا يمكن حذف الخطة المستخدمة في خدمات التصميم"
            )
        plan.delete()
        response_data = message(
            en="Plan deleted successfully",
            ar="تم حذف الخطة بنجاح",
            status="success"
        )
        return Response(response_data, status=status.HTTP_200_OK) 