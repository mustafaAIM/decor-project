from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, timedelta
from django.utils import timezone
from zoneinfo import ZoneInfo

from ..models import ConsultingService, ServiceOrder
from ..serializers.consulting_service_serializer import ConsultingServiceSerializer
from customer.permissions import IsCustomer
from employee.models import Employee, WorkingHours
from django.conf import settings

class ConsultingServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ConsultingServiceSerializer
    permission_classes = [IsCustomer]
    lookup_field = 'uuid'

    def get_queryset(self):
        return ConsultingService.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def available_slots(self, request):
        consultant_uuid = request.query_params.get('consultant_uuid')
        date_str = request.query_params.get('date')
        duration = int(request.query_params.get('duration', 60))

        if not all([consultant_uuid, date_str]):
            return Response({
                "error": "consultant_uuid and date are required"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            consultant = Employee.objects.get(uuid=consultant_uuid, is_consultable=True)
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except (Employee.DoesNotExist, ValueError):
            return Response({
                "error": "Invalid consultant_uuid or date format"
            }, status=status.HTTP_400_BAD_REQUEST)

        current_timezone = ZoneInfo(settings.TIME_ZONE)

        day_name = date.strftime('%A').lower()
        working_hours = WorkingHours.objects.filter(
            employee=consultant,
            day=day_name
        ).first()

        if not working_hours:
            return Response({"slots": []})

        existing_consultations = ConsultingService.objects.filter(
            consultant=consultant,
            scheduled_date=date,
            status__in=['processing']
        ).order_by('scheduled_time')

        busy_periods = []        
        for consultation in existing_consultations:
            start = timezone.make_aware(
                datetime.combine(date, consultation.scheduled_time),
                timezone=current_timezone
            )
            end = start + timedelta(minutes=consultation.duration)
            busy_periods.append((start, end))

        current_time = timezone.make_aware(
            datetime.combine(date, working_hours.from_hour),
            timezone=current_timezone
        )
        end_time = timezone.make_aware(
            datetime.combine(date, working_hours.to_hour),
            timezone=current_timezone
        )

        if date == timezone.now().date():
            now = timezone.now()
            minutes = (now.minute // duration) * duration + duration
            next_slot = now.replace(minute=minutes, second=0, microsecond=0)
            if minutes >= 60:
                next_slot = next_slot.replace(hour=next_slot.hour + 1, minute=minutes % 60)
            current_time = max(current_time, next_slot)

        available_slots = []
        while current_time + timedelta(minutes=duration) <= end_time:
            slot_end = current_time + timedelta(minutes=duration)
            is_available = True

            for busy_start, busy_end in busy_periods:
                if current_time < busy_end and slot_end > busy_start:
                    is_available = False
                    current_time = busy_end
                    break
                      
            if is_available:
                available_slots.append({
                    'time': current_time.strftime('%H:%M'),
                    'end_time': slot_end.strftime('%H:%M')
                })
                current_time += timedelta(minutes=duration)
            
        return Response({
            "slots": available_slots,
            "working_hours": {
                "from": working_hours.from_hour.strftime('%H:%M'),
                "to": working_hours.to_hour.strftime('%H:%M')
            }
        })

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        consulting_service = serializer.save(
            user=request.user,
            title="Consulting Service"
        )
        content_type = ContentType.objects.get_for_model(ConsultingService)
        service_order = ServiceOrder.objects.create(
            customer=request.user.customer,
            service_number=f"CS-{consulting_service.uuid.hex[:8]}",
            content_type=content_type,
            object_id=consulting_service.uuid,
            amount=0,
            status=ServiceOrder.ServiceStatus.PENDING
        )

        return Response({
            'service_order_uuid': service_order.uuid
        }, status=status.HTTP_201_CREATED) 