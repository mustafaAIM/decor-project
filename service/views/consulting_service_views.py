from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, timedelta
from decimal import Decimal
from ..models import ConsultingService, ServiceOrder
from ..serializers.consulting_service_serializer import ConsultingServiceSerializer
from customer.permissions import IsCustomer
from employee.models import Employee, WorkingHours
from ..models.service_settings_model import ServiceSettings

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

        day_name = date.strftime('%A').lower()
        working_hours = WorkingHours.objects.filter(
            employee=consultant,
            day=day_name
        ).first()

        if not working_hours:
            return Response({
                "slots": [],
                "message": f"No working hours defined for {day_name}"
            })

        existing_consultations = ConsultingService.objects.filter(
            consultant=consultant,
            scheduled_date=date,
            status__in=['processing']
        ).order_by('scheduled_time')

        busy_periods = []        
        for consultation in existing_consultations:
            start = datetime.combine(date, consultation.scheduled_time)
            end = start + timedelta(minutes=consultation.duration)
            busy_periods.append((start, end))

        current_time = datetime.combine(date, working_hours.from_hour)
        end_time = datetime.combine(date, working_hours.to_hour)

        if date == datetime.now().date():
            now = datetime.now()
            total_minutes = ((now.minute // duration) + 1) * duration
            hours_to_add = total_minutes // 60
            remaining_minutes = total_minutes % 60
            
            next_slot = now.replace(minute=0, second=0, microsecond=0)
            if hours_to_add > 0:
                next_slot = next_slot.replace(hour=now.hour + hours_to_add)
            next_slot = next_slot.replace(minute=remaining_minutes)
            
            current_time = max(current_time, next_slot)

        available_slots = []
        while current_time + timedelta(minutes=duration) <= end_time:
            slot_end = current_time + timedelta(minutes=duration)
            is_available = True
            for busy_start, busy_end in busy_periods:
                if (current_time >= busy_start and current_time < busy_end) or \
                   (slot_end > busy_start and slot_end <= busy_end) or \
                   (current_time <= busy_start and slot_end >= busy_end):
                    is_available = False
                    current_time = busy_end  
                    break
                      
            if is_available:
                available_slots.append({
                    'time': current_time.strftime('%H:%M'),
                    'end_time': slot_end.strftime('%H:%M'),
                    'duration': duration
                })
                current_time += timedelta(minutes=duration)
            
        return Response({
            "slots": available_slots,
            "working_hours": {
                "from": working_hours.from_hour.strftime('%H:%M'),
                "to": working_hours.to_hour.strftime('%H:%M')
            },
            "date": date_str,
            "busy_periods": [ 
                {
                    "start": bp[0].strftime('%H:%M'),
                    "end": bp[1].strftime('%H:%M')
                } for bp in busy_periods
            ]
        })

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        consulting_service = serializer.save(
            user=request.user,
            title="Consulting Service"
        )
        
        duration_minutes = serializer.validated_data.get('duration', 60)
        
        service_settings = ServiceSettings.get_settings()
        
        amount = Decimal(duration_minutes) / Decimal('60.0') * service_settings.consulting_hourly_rate
        
        content_type = ContentType.objects.get_for_model(ConsultingService)
        service_order = ServiceOrder.objects.create(
            customer=request.user.customer,
            service_number=f"CS-{consulting_service.uuid.hex[:8]}",
            content_type=content_type,
            object_id=consulting_service.id,
            amount=amount,
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
            'paid': False,
            'type': 'consultingservice'
        }

        return Response(response_data, status=status.HTTP_201_CREATED) 