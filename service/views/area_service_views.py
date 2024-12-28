from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import transaction
from django.contrib.contenttypes.models import ContentType

from ..models import AreaService, ServiceOrder
from ..serializers.area_service_serializer import AreaServiceSerializer
from customer.permissions import IsCustomer
from ..models.service_settings_model import ServiceSettings

class AreaServiceViewSet(viewsets.ModelViewSet):
    serializer_class = AreaServiceSerializer
    permission_classes = [IsCustomer]
    lookup_field = 'uuid'

    def get_queryset(self):
        return AreaService.objects.filter(user=self.request.user)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        area_service = serializer.save(
            user=request.user,
            title="Area Service"
        )
        service_settings = ServiceSettings.get_settings()
        content_type = ContentType.objects.get_for_model(AreaService)
        service_order = ServiceOrder.objects.create(
            customer=request.user.customer,
            service_number=f"AS-{area_service.uuid.hex[:8]}",
            content_type=content_type,
            object_id=area_service.id,
            amount=service_settings.area_service_cost,
            status=ServiceOrder.ServiceStatus.PENDING
        )

        return Response({
            'service_order_uuid': service_order.uuid
        }, status=status.HTTP_201_CREATED) 