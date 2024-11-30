from django.db import models
from utils.models import TimeStampedModel
from product.models import ProductColor
from .order_model import Order

class OrderItem(TimeStampedModel):
    order = models.ForeignKey(
        Order, 
        related_name='items', 
        on_delete=models.CASCADE
    )
    product_color = models.ForeignKey(
        ProductColor, 
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['product_color']),
        ]

    @property
    def subtotal(self):
        return self.quantity * self.price