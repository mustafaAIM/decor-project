from django.urls import path, include
from rest_framework.routers import DefaultRouter
from section.views import SectionViewSet , CategoryViewSet

router = DefaultRouter()
router.register(r'sections', SectionViewSet)
router.register(r'category',CategoryViewSet)
urlpatterns = [
    path('', include(router.urls)),
]