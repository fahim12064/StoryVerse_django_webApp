import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Post, Comment, Like


class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.post_id = self.scope["url_route"]["kwargs"]["post_id"]
        self.post_group_name = f'post_{self.post_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.post_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.post_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']
        
        if action == 'add_comment':
            comment_data = await self.add_comment(text_data_json)
            # Send comment to room group
            await self.channel_layer.group_send(
                self.post_group_name,
                {
                    'type': 'comment_message',
                    'comment_data': comment_data
                }
            )
    
    async def comment_message(self, event):
        comment_data = event['comment_data']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'comment',
            'comment_data': comment_data
        }))
    
    @database_sync_to_async
    def add_comment(self, data):
        try:
            post_id = data['post_id']
            content = data['content']
            parent_id = data.get('parent_id', None)
            
            post = Post.objects.get(id=post_id)
            author = self.scope["user"]
            
            if parent_id:
                parent = Comment.objects.get(id=parent_id)
                comment = Comment.objects.create(post=post, author=author, content=content, parent=parent)
                
                # Create notification for reply
                if parent.author != author:
                    from notifications.models import Notification
                    Notification.objects.create(
                        recipient=parent.author,
                        sender=author,
                        notification_type='reply',
                        text=f'{author.username} replied to your comment',
                        related_object_id=comment.id
                    )
            else:
                comment = Comment.objects.create(post=post, author=author, content=content)
                
                # Create notification for comment
                if post.author != author:
                    from notifications.models import Notification
                    Notification.objects.create(
                        recipient=post.author,
                        sender=author,
                        notification_type='comment',
                        text=f'{author.username} commented on your post',
                        related_object_id=comment.id
                    )
            
            # Update points
            author.profile.points += 3
            author.profile.save()
            
            return {
                'id': comment.id,
                'author': comment.author.username,
                'author_id': comment.author.id,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%B %d, %Y, %I:%M %p'),
                'parent_id': comment.parent.id if comment.parent else None,
                'avatar': comment.author.profile.profile_picture.url if comment.author.profile.profile_picture else None
            }
        except Exception as e:
            return {'error': str(e)}


class LikeConsumer(AsyncWebsocketConsumer):
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
        post_id = text_data_json['post_id']
        
        if action == 'like':
            result = await self.like_post(post_id)
        elif action == 'unlike':
            result = await self.unlike_post(post_id)
        
        await self.send(text_data=json.dumps(result))
    
    @database_sync_to_async
    def like_post(self, post_id):
        try:
            post = Post.objects.get(id=post_id)
            like, created = Like.objects.get_or_create(post=post, user=self.user)
            
            if created:
                # Update points
                post.author.profile.points += 2
                post.author.profile.save()
                
                # Create notification
                if post.author != self.user:
                    from notifications.models import Notification
                    Notification.objects.create(
                        recipient=post.author,
                        sender=self.user,
                        notification_type='like',
                        text=f'{self.user.username} liked your post',
                        related_object_id=post.id
                    )
                
                return {
                    'status': 'success',
                    'message': 'You liked this post',
                    'likes_count': post.likes.count()
                }
            else:
                return {
                    'status': 'info',
                    'message': 'You already liked this post',
                    'likes_count': post.likes.count()
                }
        except Post.DoesNotExist:
            return {'status': 'error', 'message': 'Post not found'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    @database_sync_to_async
    def unlike_post(self, post_id):
        try:
            post = Post.objects.get(id=post_id)
            deleted, _ = Like.objects.filter(post=post, user=self.user).delete()
            
            if deleted:
                # Update points
                post.author.profile.points = max(0, post.author.profile.points - 2)
                post.author.profile.save()
                
                return {
                    'status': 'success',
                    'message': 'You unliked this post',
                    'likes_count': post.likes.count()
                }
            else:
                return {
                    'status': 'info',
                    'message': 'You did not like this post',
                    'likes_count': post.likes.count()
                }
        except Post.DoesNotExist:
            return {'status': 'error', 'message': 'Post not found'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}