from django.db import models
from .base_service_model import BaseService
from employee.models import Employee
from .service_method_model import ServiceMethod
import uuid

class ConsultingService(BaseService):
    consultant = models.ForeignKey(Employee, on_delete=models.CASCADE)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    duration = models.IntegerField(help_text="Duration in minutes")
    method = models.ForeignKey(ServiceMethod, on_delete=models.PROTECT)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return f"Consulting Service - {self.title}"

    class Meta:
        indexes = [
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['consultant']),
        ] 


        