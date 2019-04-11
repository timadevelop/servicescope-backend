# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery.decorators import periodic_task
from datetime import datetime
import requests

from saasrest.settings import SAAS_REALTIME_NOTIFICATION_URL

from .models import Event, Notification
from .serializers import EventSerializer, NotificationSerializer

# just a test shared task
# @shared_task
# def add(x, y):
#     return x + y



def send_notification(notification):
    if not notification or not getattr(notification, 'recipient', False):
        return False
    serializer = NotificationSerializer(notification, many=False, context = {'request': None})
    resp = requests.post(SAAS_REALTIME_NOTIFICATION_URL, serializer.data)
    if resp.json()['notified']:
        return True
    else:
        # well, user may be not connected or some different reason why
        # he was not notified, no updates to DB, maybe later.
        # print('not notified')
        return False


# TODO: change to every 60 seconds
@periodic_task(run_every=10.0, name="process_events", ignore_result=True)
def process_events():
    events = Event.objects.filter(notification_datetime__lte=datetime.now(), notified=False)
    for event in events:
        try:
            notification = Notification()
            notification.title = 'Hey, {} is soon!'.format(event.title)
            notification.redirect_url = '/events/{}'.format(event.id)
            notification.text = '{} is starting on {}'.format(event.title, event.notification_datetime.strftime("%d %B %Y %I:%M:%S %p"))
            # Notify doctor
            notification.recipient = event.doctor.profile
            if send_notification(notification):
                event.notified = True
                event.save(update_fields=['notified'])

            # Notify patient
            notification.recipient = getattr(event.patient, 'profile', None)
            if send_notification(notification):
                event.notified = True
                event.save(update_fields=['notified'])
        except requests.exceptions.RequestException as e:
            # well, we could not connect
            print(e)
            return False
    return True


# TODO: change to every 60 seconds
@periodic_task(run_every=10.0, name="process_notifications", ignore_result=True)
def process_notifications():
    notifications = Notification.objects.filter(notification_datetime__lte=datetime.now(), notified=False)
    for notification in notifications:
        try:
            if send_notification(notification):
                notification.notified = True
                # notification.save(update_fields=['notified'])
                # print('sent:', notification.notified)
                notification.delete()
        except requests.exceptions.RequestException as e:
            # well, we could not connect
            print(e)
            return False
    return True



