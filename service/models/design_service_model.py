from file_management.base_model import BaseFile
from django.db import models
from .base_service_model import BaseService, ContactInfo
from section.models import Section
from plan.models import Plan
from product.models import Color
import uuid

class DesignService(BaseService, ContactInfo):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    area = models.DecimalField(max_digits=10, decimal_places=4)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    prefered_colors = models.ManyToManyField(Color, blank=True)

    def __str__(self):
        return f"Design Service - {self.title}"


class DesignServiceFile(BaseFile):
    FILE_TYPE_CHOICES = (
        ('area_file', 'Area File'),
        ('inspiration', 'Inspiration Image'),
    )
    
    service = models.ForeignKey(
        DesignService,
        on_delete=models.CASCADE,
        related_name='files'
    )
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    class Meta:
        indexes = [
            models.Index(fields=['service']),
            models.Index(fields=['file_type']),
        ]