from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views.design_service_views import DesignServiceViewSet
from ..views.service_settings_views import ServiceSettingsViewSet
from ..views.area_service_views import AreaServiceViewSet
from ..views.consulting_service_views import ConsultingServiceViewSet
from ..views.service_method_views import ServiceMethodViewSet

router = DefaultRouter()
router.register(r'design-services', DesignServiceViewSet, basename='design-service')
router.register(r'service-settings', ServiceSettingsViewSet, basename='service-settings')
router.register(r'area-services', AreaServiceViewSet, basename='area-service')
router.register(r'consulting-services', ConsultingServiceViewSet, basename='consulting-service')
router.register(r'service-methods', ServiceMethodViewSet, basename='service-method')

urlpatterns = [
    path('', include(router.urls)),
]
