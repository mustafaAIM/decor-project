from django.db import models
from django.conf import settings

class BaseService(models.Model):
    # STATUS_CHOICES = (
    #     ('pending', 'Pending'),
    #     ('in_progress', 'In Progress'),
    #     ('completed', 'Completed'),
    #     ('cancelled', 'Cancelled'),
    # )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        abstract = True


class ContactInfo(models.Model):
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    class Meta:
        abstract = True

