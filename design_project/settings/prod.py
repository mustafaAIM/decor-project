from .base import *

DEBUG = False
ALLOWED_HOSTS = ['your-production-domain.com']

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
