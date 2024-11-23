from django.db import models
from django.conf import settings
import uuid

class Payment(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    )
    
    PAYMENT_TYPE = (
        ('product', 'Product Order'),
        ('service', 'Service Order')
    )
    
    PAYMENT_METHOD = (
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal')
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)
    payment_intent_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ProductOrder(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='product_order')
    
class ServiceOrder(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.models.CASCADE, related_name='service_order')
    service_type = models.CharField(max_length=50)  # DesignService, AreaService, etc.
    service_id = models.IntegerField()