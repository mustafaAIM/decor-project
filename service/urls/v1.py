from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views.design_service_views import DesignServiceViewSet

router = DefaultRouter()
router.register(r'design-services', DesignServiceViewSet, basename='design-service')

urlpatterns = [
    path('', include(router.urls)),
]
