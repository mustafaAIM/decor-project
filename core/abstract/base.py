from django.db import models
from core.mixins.models import UUIDMixin, SoftDeleteMixin, AuditMixin, StatusMixin
from django.utils import timezone

class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    'created_at' and 'updated_at' fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True 




class BaseModel(UUIDMixin, SoftDeleteMixin, AuditMixin , TimeStampedModel):
    class Meta:
        abstract = True

class BaseStatusModel(BaseModel, StatusMixin):
    class Meta:
        abstract = True
