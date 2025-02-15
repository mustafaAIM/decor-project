from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from typing import Any
from django.contrib.auth import get_user_model

User = get_user_model()

class NotificationService:
    @staticmethod
    def send_notification(sender: User, receiver: User, message: str) -> Any:
        from notification.models.notification_model import Notification
        notification = Notification.objects.create(
            sender=sender,
            receiver=receiver,
            message=message,
            is_read=False
        )
        
        channel_layer = get_channel_layer()
        group_name = f'user_{receiver.id}'
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'send_notification',
                'notification': message
            }
        )
        
        return notification

    @classmethod
    def notify_admins(cls, sender: User, message: str) -> None:
        admin_users = User.objects.filter(role=User.Role.ADMIN)
        for admin in admin_users:
            cls.send_notification(
                sender=sender,
                receiver=admin,
                message=message
            ) 