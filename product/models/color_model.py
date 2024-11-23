from django.db import models
import uuid

class Color(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    hex_code = models.CharField(max_length=7)

    def __str__(self):
        return self.hex_code