from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
from django.contrib.contenttypes.models import ContentType

from ..models import DesignService, DesignServiceFile, ServiceOrder
from ..serializers.design_service_serializer import (
    DesignServiceSerializer,
    DesignServiceFileSerializer
)
from customer.permissions import IsCustomer
from utils import BadRequestError

class DesignServiceViewSet(viewsets.ModelViewSet):
    serializer_class = DesignServiceSerializer
    permission_classes = [IsCustomer]
    parser_classes = (MultiPartParser, FormParser)
    lookup_field = 'uuid'

    def get_queryset(self):
        return DesignService.objects.filter(user=self.request.user)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        design_service = serializer.save(
            user=request.user,
            title="Design Service"
        )
        
        content_type = ContentType.objects.get_for_model(DesignService)
        service_order = ServiceOrder.objects.create(
            customer=request.user.customer,
            service_number=f"DS-{design_service.uuid.hex[:8]}",
            content_type=content_type,
            object_id=design_service.id,
            amount=design_service.plan.price * design_service.area,
            status=ServiceOrder.ServiceStatus.PENDING
        )

        response_data = {
            'uuid': service_order.uuid,
            'reference_number': service_order.service_number,
            'customer': service_order.customer.id,
            'order_number': service_order.service_number,
            'status': service_order.status,
            'total_amount': float(service_order.amount),
            'notes': service_order.notes,
            'isPaid': False,
            'type': 'designservice'
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_files(self, request, uuid=None):
        design_service = self.get_object()
        files = request.FILES.getlist('files', [])
        file_type = request.data.get('file_type')

        if not file_type in ['area_file', 'inspiration']:
            raise BadRequestError(
                en_message="Invalid file type",
                ar_message="نوع الملف غير صالح"
            )

        created_files = []
        for file in files:
            service_file = DesignServiceFile.objects.create(
                service=design_service,
                file=file,
                file_type=file_type
            )
            created_files.append(service_file)

        serializer = DesignServiceFileSerializer(created_files, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def remove_file(self, request, uuid=None):
        design_service = self.get_object()
        file_uuid = request.data.get('file_uuid')

        try:
            file = DesignServiceFile.objects.get(
                uuid=file_uuid,
                service=design_service
            )
            file.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except DesignServiceFile.DoesNotExist:
            raise BadRequestError(
                en_message="File not found",
                ar_message="الملف غير موجود"
            )
