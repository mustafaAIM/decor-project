from django.db import models
from payment.models import Payment
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class ServicePayment(Payment):
    CONTENT_TYPES = models.Q(app_label='services', model='designservice') | \
                    models.Q(app_label='services', model='areaservice') | \
                    models.Q(app_label='services', model='consultingservice')
    
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=CONTENT_TYPES
    )
    object_id = models.UUIDField()
    service = GenericForeignKey('content_type', 'object_id')