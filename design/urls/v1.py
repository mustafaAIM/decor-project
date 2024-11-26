from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views.design_view import DesignViewSet

router = DefaultRouter()
router.register(r'designs', DesignViewSet)

urlpatterns = [
    path('', include(router.urls)),
]