# rest framework
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
# models
from ..models.notification_model import Notification
# serializers
from ..serializers.notification_serializer import NotificationSerializer

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class NotificationViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Notification.objects.filter(receiver=self.request.user).order_by('-is_read', '-created_at')

    def list(self, request):
        # Retrieve notifications for the authenticated user
        notifications = Notification.objects.filter(receiver=request.user).order_by('-is_read', '-created_at')

        # Mark notifications as read
        notifications.update(is_read=True)

        # Serialize the notifications
        serializer = NotificationSerializer(notifications, many=True)
        
        return Response(serializer.data)