import os
from .base import *

env = os.getenv('DJANGO_ENV', 'development')

if env == 'development':
    from .dev import *
elif env == 'production':
    from .prod import *
else:
    raise ValueError('Invalid DJANGO_ENV environment variable')
