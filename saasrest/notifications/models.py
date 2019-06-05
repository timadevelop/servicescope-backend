from django.db import models
from django.utils.timezone import now

from authentication.models import User
from messaging.models import Conversation


class Notification(models.Model):
    """Notification model"""
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications')
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)

    title = models.TextField(max_length=30)
    text = models.TextField(max_length=150)
    notification_datetime = models.DateTimeField(default=now, blank=False)
    notified = models.BooleanField(default=False)
    redirect_url = models.TextField(max_length=20, blank=True)
    type = models.TextField(max_length=30, default="info")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """override save"""
        # set notified to false on instance update
        if 'update_fields' not in kwargs or 'notified' not in kwargs['update_fields']:
            self.notified = False
        super(Notification, self).save(*args, **kwargs)
