from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', 'app', '45.9.191.191']

STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/static/'  
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/media/' 

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_CREDENTIALS = True