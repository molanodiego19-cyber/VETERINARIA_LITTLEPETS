import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'veterinaria.settings')

app = Celery('veterinaria')

# Lee configuración desde settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descubre tasks automáticamente
app.autodiscover_tasks()

CELERY_BROKER_USE_SSL = {
    'ssl_cert_reqs': None
}