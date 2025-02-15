from django.db import models
from django.contrib.auth import get_user_model
import uuid
from customer.models.customer_model import Customer

class Cart(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.uuid} - {self.customer.user.email}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def unique_items(self):
        return self.items.count()

    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items.all())

class CartItem(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product_color = models.ForeignKey('product.ProductColor', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cart', 'product_color')

    def __str__(self):
        return f"{self.product_color.product.name} - {self.quantity}"

    @property
    def subtotal(self):
        return self.quantity * self.product_color.price