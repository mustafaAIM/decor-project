"""
ASGI config for design_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from urllib.parse import parse_qs

# Set Django settings module first
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "design_project.settings")

# Initialize Django ASGI application first
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

# Import Django and Channels components after Django is initialized
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
# notifications
from notification.urls.ws_v1 import websocket_urlpatterns
from notification.middleware.notifications_middleware import JWTAuthMiddleware

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddleware(
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    )
})