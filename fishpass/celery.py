from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marineplanner.settings')

app = Celery('marineplanner', backend='amqp', broker='amqp://guest@localhost//', include=['fishpass.tasks'])

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

if __name__ == '__main__':
    app.stsart()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

@app.task(bind=True)
def run_view(self, module_name, view_name, *args):
    # RDH: Not sure why I have to add '.views' to the below for the module to know it has 'views'.
    module = __import__('%s.views' % module_name)
    view = getattr(module.views, view_name)
    return view(*args)
