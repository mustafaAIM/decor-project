from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views.design_view import DesignViewSet
from ..views.design_file_view import DesignFileViewSet

router = DefaultRouter()
router.register(r'designs', DesignViewSet, basename='design')
router.register(r'design-files', DesignFileViewSet, basename='design-file')

urlpatterns = [
    path('', include(router.urls)),
]