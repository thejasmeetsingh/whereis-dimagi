import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whereis.settings')

app = Celery('whereis.settings')
app.config_from_object(
    'django.conf:settings',
    force=True,
    namespace='CELERY'
)
app.autodiscover_tasks(['api'])
