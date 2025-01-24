from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from advertisement.models import Advertisement
from advertisement.serializers.advertisement_serializer import AdvertisementSerializer

class AdvertisementViewSet(viewsets.ModelViewSet):
    queryset = Advertisement.objects.filter(is_active=True)
    serializer_class = AdvertisementSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'uuid' 