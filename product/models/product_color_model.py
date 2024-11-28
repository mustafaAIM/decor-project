from django.db import models
# models
from .product_model import Product
from .color_model import Color

import uuid

class ProductColor(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    product = models.ForeignKey(Product, related_name='product_colors', on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()

    class Meta:
        unique_together = ('product', 'color')

    def __str__(self):
        return f'{self.product.name} - {self.color.hex_code}'