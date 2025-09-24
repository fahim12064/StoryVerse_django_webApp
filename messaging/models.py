from django.db import models
from django.contrib.auth.models import User


class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Conversation {self.id}"
    
    @property
    def last_message(self):
        return self.messages.order_by('-created_at').first()
    
    @property
    def unread_count(self, user):
        return self.messages.filter(recipient=user, is_read=False).count()


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f'Message from {self.sender.username} to {self.recipient.username}'
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()