from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views.design_service_views import DesignServiceViewSet
from ..views.supervision_service_views import SupervisionServiceViewSet
from ..views.implementaion_service_views import ImplementaionServiceViewSet

router = DefaultRouter()
router.register(r'design-services', DesignServiceViewSet, basename='design-service')
router.register(r'supervision-service', SupervisionServiceViewSet, basename='supervision-service')
router.register(r'implementaion-service', ImplementaionServiceViewSet, basename='implementaion-service')

urlpatterns = [
    path('', include(router.urls)),
]
