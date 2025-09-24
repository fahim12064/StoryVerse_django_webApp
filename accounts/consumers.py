import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Profile, Follow


class FollowConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
        else:
            await self.accept()
    
    async def disconnect(self, close_code):
        pass
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']
        user_id = text_data_json['user_id']
        
        if action == 'follow':
            result = await self.follow_user(user_id)
        elif action == 'unfollow':
            result = await self.unfollow_user(user_id)
        
        await self.send(text_data=json.dumps(result))
    
    @database_sync_to_async
    def follow_user(self, user_id):
        try:
            user_to_follow = User.objects.get(id=user_id)
            profile, created = Profile.objects.get_or_create(user=user_to_follow)
            
            # Create follow relationship
            Follow.objects.get_or_create(follower=self.user, following=user_to_follow)
            
            # Update points
            profile.points += 5
            profile.save()
            
            # Create notification
            from notifications.models import Notification
            Notification.objects.create(
                recipient=user_to_follow,
                sender=self.user,
                notification_type='follow',
                text=f'{self.user.username} started following you'
            )
            
            return {
                'status': 'success',
                'message': 'You are now following this user',
                'followers_count': profile.followers.count()
            }
        except User.DoesNotExist:
            return {'status': 'error', 'message': 'User not found'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    @database_sync_to_async
    def unfollow_user(self, user_id):
        try:
            user_to_unfollow = User.objects.get(id=user_id)
            profile = Profile.objects.get(user=user_to_unfollow)
            
            # Remove follow relationship
            Follow.objects.filter(follower=self.user, following=user_to_unfollow).delete()
            
            # Update points
            profile.points = max(0, profile.points - 5)
            profile.save()
            
            return {
                'status': 'success',
                'message': 'You have unfollowed this user',
                'followers_count': profile.followers.count()
            }
        except User.DoesNotExist:
            return {'status': 'error', 'message': 'User not found'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}