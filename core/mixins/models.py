from django.db import models
from django.utils import timezone
from typing import Any

class SoftDeleteMixin(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def delete(self, using: Any = None, keep_parents: bool = False) -> None:
        self.deleted_at = timezone.now()
        self.is_deleted = True
        self.save(using=using)

    def hard_delete(self, using: Any = "default") -> None:
        super().delete(using=using)

class UUIDMixin(models.Model):
    import uuid
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        abstract = True

class StatusMixin(models.Model):
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

class AuditMixin(models.Model):
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_created',
    )
    updated_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_updated',
    )

    class Meta:
        abstract = True 
