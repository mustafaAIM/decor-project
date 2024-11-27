from file_management.base_model import BaseFile
from django.db import models
from .base_service_model import BaseService
from section.models import Section
from plan.models import Plan
from product.models import Color


class DesignService(BaseService):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    area = models.DecimalField(max_digits=10, decimal_places=4)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    prefered_colors = models.ManyToManyField(Color ,blank=True)



class DesignServiceFile(BaseFile):
    service = models.ForeignKey(
        DesignService,
        on_delete=models.CASCADE,
        related_name='files'
    )
    class Meta:
        indexes = [
            models.Index(fields=['service']),
            models.Index(fields=['file_type']),
        ]