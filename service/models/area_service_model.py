from django.db import models
from .base_service_model import BaseService, ContactInfo

class AreaService(BaseService, ContactInfo):
    def __str__(self):
        return f"Area Service - {self.title}"