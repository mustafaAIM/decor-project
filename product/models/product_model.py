# django
from django.db import models
# core
import uuid
# models
from section.models.category_model import Category

class Product(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name