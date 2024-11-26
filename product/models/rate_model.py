from django.db import models
# models
from .product_model import Product
from customer.models.customer_model import Customer

class Rate(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=2, decimal_places=1)
    
    def __str__(self):
        return f'Rating for {self.product.name} - Score: {self.score}'