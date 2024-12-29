# django
from django.conf import settings
from django.db import models
from django.utils import timezone
# core
import uuid
# models
from customer.models.customer_model import Customer
from section.models.section_model import Section
from ..models.base_service_model import ContactInfo

class SupervisionService(ContactInfo):
    TYPE_CHOICES = (
        ('daily', 'daily'),
        ('weekly', 'weekly'),
        ('monthly', 'monthly'),
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='daily')
    city = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now())
    updated_at = models.DateTimeField(default=timezone.now())

    def __str__(self):
        return self.title