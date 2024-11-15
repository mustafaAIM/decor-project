from .base import *

DEBUG = False
ALLOWED_HOSTS = ['your-production-domain.com']

STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/static/'  
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Media settings
MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/media/' 