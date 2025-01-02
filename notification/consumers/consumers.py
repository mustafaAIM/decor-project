import json
# channels
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
# models
from notification.models.notification_model import Notification

class NotificationConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_name = None
        self.user = None

    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            await self.close()
        else:
            self.group_name = f'user_{self.user.id}'
            # Join the user group
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            try:
                notifications = await self.get_unread_notifications(self.user)
                await self.send(text_data=json.dumps({
                    'message': notifications
                }))
            except Exception as e:
                print(f'Error accured {e}')
                await self.close()

    async def disconnect(self, close_code):
        # Leave the user group only if we joined one
        if self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Handle incoming messages if needed
        print(data)

    async def send_notification(self, event):
        notification = event['notification']
        await self.send(text_data=json.dumps({
            'notification': notification
        }))

    @database_sync_to_async
    def get_unread_notifications(self, user):
        notifications_number = Notification.objects.filter(receiver=user, is_read=False).count()
        return notifications_number