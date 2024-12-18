from django.db import models
import uuid
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal

class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        REFUNDED = 'REFUNDED', 'Refunded'

    class PaymentMethod(models.TextChoices):
        PAYPAL = 'PAYPAL', 'PayPal'
        STRIPE = 'STRIPE', 'Stripe'

    STRIPE_FEE_PERCENTAGE = Decimal('2.9')  # 2.9%
    STRIPE_FIXED_FEE = Decimal('0.30')      # $0.30
    PAYPAL_FEE_PERCENTAGE = Decimal('3.49')  # 3.49%
    PAYPAL_FIXED_FEE = Decimal('0.49')      # $0.49

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    payable = GenericForeignKey('content_type', 'object_id')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    payment_intent_id = models.CharField(max_length=255, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    @staticmethod
    def calculate_fees(amount, payment_method):
        """Calculate payment gateway fees"""
        amount = Decimal(str(amount))
        
        if payment_method == Payment.PaymentMethod.STRIPE:
            percentage_fee = (amount * Payment.STRIPE_FEE_PERCENTAGE) / 100
            total_fee = percentage_fee + Payment.STRIPE_FIXED_FEE
        elif payment_method == Payment.PaymentMethod.PAYPAL:
            percentage_fee = (amount * Payment.PAYPAL_FEE_PERCENTAGE) / 100
            total_fee = percentage_fee + Payment.PAYPAL_FIXED_FEE
        else:
            total_fee = Decimal('0')

        return {
            'base_amount': amount,
            'fee_amount': total_fee.quantize(Decimal('0.01')),
            'total_amount': (amount + total_fee).quantize(Decimal('0.01'))
        }

    class Meta:
        ordering = ['-created_at']