import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Notification


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
        else:
            # Join a group for this user to receive notifications
            self.user_group_name = f'notifications_{self.user.id}'
            await self.channel_layer.group_add(
                self.user_group_name,
                self.channel_name
            )
            
            await self.accept()
    
    async def disconnect(self, close_code):
        # Leave the notification group
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']
        
        if action == 'mark_read':
            notification_id = text_data_json['notification_id']
            result = await self.mark_notification_read(notification_id)
            await self.send(text_data=json.dumps(result))
        elif action == 'mark_all_read':
            result = await self.mark_all_notifications_read()
            await self.send(text_data=json.dumps(result))
    
    async def notify(self, event):
        notification_data = event['notification_data']
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification_data': notification_data
        }))
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, recipient=self.user)
            notification.mark_as_read()
            
            return {
                'status': 'success',
                'notification_id': notification.id,
                'unread_count': self.user.notifications.filter(is_read=False).count()
            }
        except Notification.DoesNotExist:
            return {'status': 'error', 'message': 'Notification not found'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    @database_sync_to_async
    def mark_all_notifications_read(self):
        try:
            unread_notifications = self.user.notifications.filter(is_read=False)
            for notification in unread_notifications:
                notification.mark_as_read()
            
            return {
                'status': 'success',
                'unread_count': 0
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}