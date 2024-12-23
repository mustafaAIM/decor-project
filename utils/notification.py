from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_notification(user, message):
    channel_layer = get_channel_layer()
    group_name = f'user_{user.id}'
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'send_notification',
            'notification': message
        }
    )