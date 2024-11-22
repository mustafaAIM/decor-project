from django.db import models
from django.utils import timezone
from customer.models import Customer
import uuid

class ComplaintStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    RESOLVED = 'RESOLVED', 'Resolved'
    CLOSED = 'CLOSED', 'Closed'

class ComplaintPriority(models.TextChoices):
    LOW = 'LOW', 'Low'
    MEDIUM = 'MEDIUM', 'Medium'
    HIGH = 'HIGH', 'High'
    URGENT = 'URGENT', 'Urgent'

class Complaint(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='complaints'
    )
    
    status = models.CharField(
        max_length=20,
        choices=ComplaintStatus.choices,
        default=ComplaintStatus.PENDING
    )

    priority = models.CharField(
        max_length=20,
        choices=ComplaintPriority.choices,
        default=ComplaintPriority.MEDIUM,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    reference_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True
    )
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"#{self.reference_number} - {self.title}"
    
      
    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = self._generate_reference_number()
        super().save(*args, **kwargs)
    
    def _generate_reference_number(self):
        year_month = timezone.now().strftime('%Y%m')
        random_string = str(uuid.uuid4()).upper()[:6]
        reference = f'COMP-{year_month}-{random_string}'
        
        while Complaint.objects.filter(reference_number=reference).exists():
            random_string = str(uuid.uuid4()).upper()[:6]
            reference = f'COMP-{year_month}-{random_string}'
        
        return reference
