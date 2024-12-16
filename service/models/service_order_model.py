from django.db import models
import uuid
from customer.models import Customer
from django.contrib.contenttypes.fields import GenericForeignKey

class ServiceOrder(models.Model):
    class ServiceStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    service_number = models.CharField(max_length=50, unique=True)
    
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.UUIDField()
    service = GenericForeignKey('content_type', 'object_id')
    
    status = models.CharField(max_length=20, choices=ServiceStatus.choices, default=ServiceStatus.PENDING)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at'] 