from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views.design_service_views import DesignServiceViewSet
from ..views.supervision_service_views import SupervisionServiceViewSet
from ..views.implementaion_service_views import ImplementaionServiceViewSet
from ..views.service_settings_views import ServiceSettingsViewSet
from ..views.area_service_views import AreaServiceViewSet
from ..views.consulting_service_views import ConsultingServiceViewSet
from ..views.service_method_views import ServiceMethodViewSet
from ..views.admin_service_views import (
    AdminServiceOrderViewSet, 
    AdminImplementationServiceViewSet,
    AdminSupervisionServiceViewSet
)

router = DefaultRouter()
router.register(r'design-services', DesignServiceViewSet, basename='design-service')
router.register(r'supervision-service', SupervisionServiceViewSet, basename='supervision-service')
router.register(r'implementaion-service', ImplementaionServiceViewSet, basename='implementaion-service')
router.register(r'service-settings', ServiceSettingsViewSet, basename='service-settings')
router.register(r'area-services', AreaServiceViewSet, basename='area-service')
router.register(r'consulting-services', ConsultingServiceViewSet, basename='consulting-service')
router.register(r'service-methods', ServiceMethodViewSet, basename='service-method')
router.register(r'admin/services', AdminServiceOrderViewSet, basename='admin-services')
router.register(r'admin/implementation-services', AdminImplementationServiceViewSet, basename='admin-implementation-services')
router.register(r'admin/supervision-services', AdminSupervisionServiceViewSet, basename='admin-supervision-services')

urlpatterns = [
    path('', include(router.urls)),
]
