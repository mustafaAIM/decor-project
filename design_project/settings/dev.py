from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', 'app']

STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/static/'  
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Media settings
MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/media/' 