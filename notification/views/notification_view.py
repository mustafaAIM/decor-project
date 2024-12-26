# rest framework
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
# models
from ..models.notification_model import Notification
# serializers
from ..serializers.notification_serializer import NotificationSerializer

class NotificationViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(receiver=self.request.user).order_by('-created_at')