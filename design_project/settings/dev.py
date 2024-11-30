from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', 'app','45.9.191.191']

STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/static/'  
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Media settings
MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/media/' 



# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://45.9.191.191",  # Your VPS IP
    "http://45.9.191.191:3000",  # If React runs on port 3000
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# If you're using credentials in requests (cookies, authorization headers)
CORS_ALLOW_CREDENTIALS = True

# Optional: If you need to allow specific headers or methods
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]