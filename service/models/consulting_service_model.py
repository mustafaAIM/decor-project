from django.db import models
from .base_service_model import BaseService
from employee.models import Employee
import uuid

class ConsultingService(BaseService):
    MEETING_METHOD_CHOICES = (
        ('on_site', 'On-site'),
        ('whatsapp', 'WhatsApp'),
    )

    consultant = models.ForeignKey(Employee, on_delete=models.CASCADE)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    duration = models.IntegerField(help_text="Duration in minutes")
    method = models.CharField(max_length=20, choices=MEETING_METHOD_CHOICES)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return f"Consulting Service - {self.title}"

    class Meta:
        indexes = [
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['consultant']),
        ] 