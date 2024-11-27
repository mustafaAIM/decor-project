# django
from django.db import models
# models
from file_management.base_model import BaseFile
from .desgin_model import Design
# uuid
import uuid

class DesignFile(BaseFile):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)    
    design = models.ForeignKey(Design, on_delete=models.CASCADE, related_name='files')