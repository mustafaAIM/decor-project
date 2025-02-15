from django.db import models
import uuid
#models 
from section.models import *

# Create your models here.
class Category(models.Model):
      uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
      section = models.ForeignKey(Section, on_delete=models.CASCADE)
      title = models.CharField(max_length=255)
      description = models.TextField(null=True,blank=True)
      image = models.ImageField(blank=True,null=True)

      def __str__(self):
            return self.title