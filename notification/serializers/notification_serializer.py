# rest framework
from rest_framework import serializers
# models
from ..models.notification_model import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'sender', 'receiver', 'message', 'is_read', 'created_at']