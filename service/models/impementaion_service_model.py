# django
from django.db import models
# core
import uuid
# models
from customer.models.customer_model import Customer
from section.models.section_model import Section
from .base_service_model import ContactInfo
# files
from file_management.base_model import BaseFile

class ImplementaionService(ContactInfo):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    start_date = models.CharField(max_length=255)
    end_date = models.CharField(max_length=255)
    area = models.CharField(max_length=255)
    city = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title

class ImplementaionServiceFile(BaseFile):
    FILE_TYPE_CHOICES = (
        ('area_file', 'Area File'),
        ('design_file', 'Design File'),
        ('inspiration', 'Inspiration Image'),
    )
    
    service = models.ForeignKey(
        ImplementaionService,
        on_delete=models.CASCADE,
        related_name='files'
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)

    class Meta:
        indexes = [
            models.Index(fields=['service']),
            models.Index(fields=['file_type']),
        ]