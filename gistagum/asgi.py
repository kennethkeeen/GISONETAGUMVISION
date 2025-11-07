"""
ASGI config for gistagum project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gistagum.settings')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# Phase 1: Basic ASGI setup - only HTTP for now
# WebSocket routing will be added in Phase 2
# This ensures the system still works with Gunicorn (WSGI) for HTTP requests
# and can optionally use Daphne (ASGI) for WebSocket support

application = django_asgi_app

# Phase 2 will add:
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from channels.security.websocket import AllowedHostsOriginValidator
# 
# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#     "websocket": AllowedHostsOriginValidator(
#         AuthMiddlewareStack(
#             URLRouter(...)
#         )
#     ),
# })

