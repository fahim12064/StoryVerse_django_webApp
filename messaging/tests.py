from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Conversation


class ConversationModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpass')
        self.user2 = User.objects.create_user(username='user2', password='testpass')
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)
    
    def test_conversation_creation(self):
        self.assertEqual(self.conversation.participants.count(), 2)
        self.assertIn(self.user1, self.conversation.participants.all())
        self.assertIn(self.user2, self.conversation.participants.all())
    
    def test_last_message(self):
        # Initially no messages
        self.assertIsNone(self.conversation.last_message)
        
        # Add a message
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            recipient=self.user2,
            content='Test message'
        )
        
        self.assertEqual(self.conversation.last_message, message)
    
    def test_unread_count(self):
        # Initially no messages
        self.assertEqual(self.conversation.unread_count(self.user1), 0)
        self.assertEqual(self.conversation.unread_count(self.user2), 0)
        
        # Add a message from user1 to user2
        Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            recipient=self.user2,
            content='Test message'
        )
        
        # user2 should have 1 unread message, user1 should have 0
        self.assertEqual(self.conversation.unread_count(self.user1), 0)
        self.assertEqual(self.conversation.unread_count(self.user2), 1)


class MessageModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpass')
        self.user2 = User.objects.create_user(username='user2', password='testpass')
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)
        self.message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            recipient=self.user2,
            content='Test message'
        )
    
    def test_message_creation(self):
        self.assertEqual(self.message.conversation, self.conversation)
        self.assertEqual(self.message.sender, self.user1)
        self.assertEqual(self.message.recipient, self.user2)
        self.assertEqual(self.message.content, 'Test message')
        self.assertFalse(self.message.is_read)
    
    def test_mark_as_read(self):
        self.assertFalse(self.message.is_read)
        self.message.mark_as_read()
        self.assertTrue(self.message.is_read)