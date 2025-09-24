from django.test import TestCase
from django.contrib.auth.models import User
from .models import Notification


class NotificationModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpass')
        self.user2 = User.objects.create_user(username='user2', password='testpass')
        self.notification = Notification.objects.create(
            recipient=self.user1,
            sender=self.user2,
            notification_type='follow',
            text=f'{self.user2.username} started following you'
        )
    
    def test_notification_creation(self):
        self.assertEqual(self.notification.recipient, self.user1)
        self.assertEqual(self.notification.sender, self.user2)
        self.assertEqual(self.notification.notification_type, 'follow')
        self.assertEqual(self.notification.text, f'{self.user2.username} started following you')
        self.assertFalse(self.notification.is_read)
    
    def test_mark_as_read(self):
        self.assertFalse(self.notification.is_read)
        self.notification.mark_as_read()
        self.assertTrue(self.notification.is_read)
    
    def test_related_post(self):
        # Initially no related post
        self.assertIsNone(self.notification.related_post)
        
        # Create a notification with a related post
        from blog.models import Post
        post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user1
        )
        
        like_notification = Notification.objects.create(
            recipient=self.user1,
            sender=self.user2,
            notification_type='like',
            text=f'{self.user2.username} liked your post',
            related_object_id=post.id
        )
        
        self.assertEqual(like_notification.related_post, post)
    
    def test_related_comment(self):
        # Initially no related comment
        self.assertIsNone(self.notification.related_comment)
        
        # Create a notification with a related comment
        from blog.models import Post, Comment
        post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user1
        )
        
        comment = Comment.objects.create(
            post=post,
            author=self.user1,
            content='Test comment'
        )
        
        reply_notification = Notification.objects.create(
            recipient=self.user1,
            sender=self.user2,
            notification_type='reply',
            text=f'{self.user2.username} replied to your comment',
            related_object_id=comment.id
        )
        
        self.assertEqual(reply_notification.related_comment, comment)