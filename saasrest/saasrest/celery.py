from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saasrest.settings')

# broker url will be loaded from settings configuration
app = Celery('saasrest')

# better use @periodictask in tasks discovered by autodiscover_tasks
# @celery_app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     # Calls every 10 seconds.
#     print('wat')
#     sender.add_periodic_task(1.0, process_notifications.s(), name='add every 10')


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
