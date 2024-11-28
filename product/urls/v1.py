from django.urls import path, include
from rest_framework.routers import DefaultRouter
# views
from ..views.product_view import ProductViewSet
from ..views.rate_view import RateViewSet , generate_product_report

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'rate', RateViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('report/', generate_product_report, name='product_report'),
]