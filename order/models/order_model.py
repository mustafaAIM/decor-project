from django.db import models
from django.conf import settings
import uuid
from customer.models import Customer
from datetime import datetime
from django.contrib.contenttypes.fields import GenericRelation
from payment.models import Payment

class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        REFUNDED = 'REFUNDED', 'Refunded'

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    reference_number = models.CharField(max_length=50, unique=True, editable=False)
    order_number = models.CharField(max_length=50, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    
    phone = models.CharField(max_length=20,null=True,blank=True)
    email = models.EmailField(null=True,blank=True)
    address = models.TextField(null=True,blank=True)
    city = models.CharField(max_length=100,null=True,blank=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    payments = GenericRelation(Payment)

    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = self.generate_reference_number()
        if not self.order_number:
            self.order_number = self.reference_number
        super().save(*args, **kwargs)

    def generate_reference_number(self):
        date_str = datetime.now().strftime('%Y%m%d')
        last_order = Order.objects.filter(
            reference_number__startswith=f'ORD-{date_str}'
        ).order_by('reference_number').last()

        if last_order:
            last_number = int(last_order.reference_number.split('-')[-1])
            new_number = str(last_number + 1).zfill(4)
        else:
            new_number = '0001'

        return f'ORD-{date_str}-{new_number}'

    def __str__(self):
        return f"Order {self.reference_number}"

class OrderItem(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_color = models.ForeignKey('product.ProductColor', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_color.product.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs) 