from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('follow', 'Follow'),
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('reply', 'Reply'),
    )
    
    recipient = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_notifications', on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    text = models.CharField(max_length=255)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Notification for {self.recipient.username}: {self.text}'
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()
    
    @property
    def related_post(self):
        if self.notification_type in ['like', 'comment'] and self.related_object_id:
            from blog.models import Post
            try:
                return Post.objects.get(id=self.related_object_id)
            except Post.DoesNotExist:
                return None
        return None
    
    @property
    def related_comment(self):
        if self.notification_type == 'reply' and self.related_object_id:
            from blog.models import Comment
            try:
                return Comment.objects.get(id=self.related_object_id)
            except Comment.DoesNotExist:
                return None
        return None