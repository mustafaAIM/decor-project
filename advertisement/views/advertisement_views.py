#rest 
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
#models
from advertisement.models import Advertisement
#serializers
from advertisement.serializers.advertisement_serializer import AdvertisementSerializer
#permissions
from admin.permissions import IsAdminOrReadOnly, IsAdmin
from utils.messages import ResponseFormatter

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
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return ResponseFormatter.success_response(data=response.data)
        
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return ResponseFormatter.success_response(data=response.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def toggle_active(self, request, uuid=None):
        advertisement = self.get_object()
        advertisement.is_active = not advertisement.is_active
        advertisement.save()
        
        response_data = {
            **ResponseFormatter.success_message(
                en="Advertisement status updated successfully",
                ar="تم تحديث حالة الإعلان بنجاح"
            ),
            "data": {"is_active": advertisement.is_active}
        }
        return Response(response_data)