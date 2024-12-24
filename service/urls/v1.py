from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views.design_service_views import DesignServiceViewSet
from ..views.service_settings_views import ServiceSettingsViewSet
from ..views.area_service_views import AreaServiceViewSet

router = DefaultRouter()
router.register(r'design-services', DesignServiceViewSet, basename='design-service')
router.register(r'service-settings', ServiceSettingsViewSet, basename='service-settings')
router.register(r'area-services', AreaServiceViewSet, basename='area-service')

urlpatterns = [
    path('', include(router.urls)),
]
