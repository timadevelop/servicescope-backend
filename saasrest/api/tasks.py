# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery.decorators import periodic_task
from django.utils import timezone

from .models import Notification
from .serializers import NotificationSerializer

from asgiref.sync import async_to_sync
from .consumers import notify_user

# def send_notification(notification):
#     if not notification or not getattr(notification, 'recipient', False):
#         return False
#     serializer = NotificationSerializer(notification, many=False, context = {'request': None})
#     async_to_sync(notify_user)(notification.recipient.id, serializer.data)

# @periodic_task(run_every=10.0, name="process_notifications", ignore_result=True)
# def process_notifications():
#     notifications = Notification.objects.filter(notification_datetime__lte=timezone.now(), notified=False)
#     for notification in notifications:
#         send_notification(notification)
#     return True
#
