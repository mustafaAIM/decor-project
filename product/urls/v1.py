from django.urls import path, include
from rest_framework.routers import DefaultRouter
# views
from ..views.product_view import ProductViewSet
from ..views.rate_view import RateViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'rate', RateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]