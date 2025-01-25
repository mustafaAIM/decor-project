from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from advertisement.models import Advertisement
from advertisement.serializers.advertisement_serializer import AdvertisementSerializer
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import PermissionDenied
from admin.permissions import IsAdminOrReadOnly
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated 
class AdvertisementPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class AdvertisementViewSet(viewsets.ModelViewSet):
    queryset = Advertisement.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = AdvertisementSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = AdvertisementPagination
    lookup_field = 'uuid'