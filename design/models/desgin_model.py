# django
from django.db import models
# core
import uuid
# models
from section.models.category_model import Category


class Design(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, related_name='designs', on_delete=models.CASCADE)

    def __str__(self):
        return self.title
