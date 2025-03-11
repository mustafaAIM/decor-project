#rest 
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
#models
from advertisement.models import Advertisement
#serializers
from advertisement.serializers.advertisement_serializer import AdvertisementSerializer
#permissions
from admin.permissions import IsAdminOrReadOnly

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