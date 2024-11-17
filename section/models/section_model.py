from django.db import models
import uuid

# Create your models here.
class Section(models.Model):
      uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
      title = models.CharField(max_length=255)
      description = models.TextField(blank=True)
      image = models.ImageField(blank=True,null=True)


