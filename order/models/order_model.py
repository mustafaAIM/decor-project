from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone
from utils.models import TimeStampedModel

class Order(TimeStampedModel):
    class OrderStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PAYMENT_PENDING = 'PAYMENT_PENDING', 'Payment Pending'
        PAID = 'PAID', 'Paid'
        PROCESSING = 'PROCESSING', 'Processing'
        SHIPPED = 'SHIPPED', 'Shipped'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'
        REFUNDED = 'REFUNDED', 'Refunded'

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT,
        related_name='orders'
    )
    order_number = models.CharField(max_length=50, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )
    
    shipping_address = models.TextField()
    phone_number = models.CharField(max_length=20)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['status']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def _generate_order_number(self):
        year_month = timezone.now().strftime('%Y%m')
        random_string = str(uuid.uuid4()).upper()[:6]
        return f'ORD-{year_month}-{random_string}'