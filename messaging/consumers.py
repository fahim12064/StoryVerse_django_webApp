import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message, Conversation


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
        else:
            # Join a general group for this user to receive notifications
            self.user_group_name = f'user_{self.user.id}'
            await self.channel_layer.group_add(
                self.user_group_name,
                self.channel_name
            )
            
            await self.accept()
    
    async def disconnect(self, close_code):
        # Leave the user group
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']
        
        if action == 'send_message':
            message_data = await self.send_message(text_data_json)
            # Send message to recipient
            recipient_id = message_data['recipient_id']
            recipient_group_name = f'user_{recipient_id}'
            await self.channel_layer.group_send(
                recipient_group_name,
                {
                    'type': 'chat_message',
                    'message_data': message_data
                }
            )
            # Also send back to sender to confirm
            await self.send(text_data=json.dumps({
                'type': 'message_sent',
                'message_data': message_data
            }))
        elif action == 'mark_read':
            await self.mark_messages_read(text_data_json)
    
    async def chat_message(self, event):
        message_data = event['message_data']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message_data': message_data
        }))
    
    @database_sync_to_async
    def send_message(self, data):
        try:
            recipient_id = data['recipient_id']
            content = data['content']
            
            recipient = User.objects.get(id=recipient_id)
            
            # Get or create conversation
            conversations = Conversation.objects.filter(participants=self.user).filter(participants=recipient)
            if conversations.exists():
                conversation = conversations.first()
            else:
                conversation = Conversation.objects.create()
                conversation.participants.add(self.user, recipient)
            
            # Create message
            message = Message.objects.create(
                conversation=conversation,
                sender=self.user,
                recipient=recipient,
                content=content
            )
            
            return {
                'id': message.id,
                'conversation_id': conversation.id,
                'sender_id': message.sender.id,
                'sender_username': message.sender.username,
                'recipient_id': message.recipient.id,
                'content': message.content,
                'is_read': message.is_read,
                'created_at': message.created_at.strftime('%B %d, %Y, %I:%M %p'),
                'sender_avatar': message.sender.profile.profile_picture.url if message.sender.profile.profile_picture else None
            }
        except User.DoesNotExist:
            return {'error': 'Recipient not found'}
        except Exception as e:
            return {'error': str(e)}
    
    @database_sync_to_async
    def mark_messages_read(self, data):
        try:
            conversation_id = data['conversation_id']
            conversation = Conversation.objects.get(id=conversation_id)
            
            # Mark all messages from the other user as read
            Message.objects.filter(
                conversation=conversation,
                recipient=self.user,
                is_read=False
            ).update(is_read=True)
            
            return {'status': 'success'}
        except Conversation.DoesNotExist:
            return {'error': 'Conversation not found'}
        except Exception as e:
            return {'error': str(e)}