import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'design_project.settings.dev')  # Change to 'prod' for production

app = Celery('design_project')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()