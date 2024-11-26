# django
from django.db import models
# models
from file_management.base_model import BaseFile
from .desgin_model import Design

class DesignFile(BaseFile):
    design = models.ForeignKey(Design, on_delete=models.CASCADE, related_name='files')