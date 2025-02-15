from django.db import models
import uuid

class Advertisement(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title_ar = models.CharField(max_length=255, verbose_name='Arabic Title'  , null=True, blank=True)
    title_en = models.CharField(max_length=255, verbose_name='English Title', null=True, blank=True)
    description_ar = models.TextField(verbose_name='Arabic Description', null=True, blank=True)
    description_en = models.TextField(verbose_name='English Description', null=True, blank=True)
    image = models.ImageField(upload_to='advertisements/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title_en 