from django.db import models

class ServiceSettings(models.Model):
    area_service_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Cost per square meter for area service"
    )
    consulting_hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Cost per hour for consulting service",
        default=0
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Service Settings'
        verbose_name_plural = 'Service Settings'

    @classmethod
    def get_settings(cls):
        settings = cls.objects.first()
        if not settings:
            settings = cls.objects.create(
                area_service_cost=0,
                consulting_hourly_rate=0
            )
        return settings