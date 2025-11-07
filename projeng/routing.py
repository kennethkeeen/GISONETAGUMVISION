"""
WebSocket URL routing for Django Channels (Phase 2: Parallel to SSE)
Defines WebSocket URL patterns for real-time updates
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # WebSocket endpoint for user-specific notifications
    # URL: ws://your-domain/ws/notifications/
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
    
    # WebSocket endpoint for project updates (all authorized users)
    # URL: ws://your-domain/ws/projects/
    re_path(r'ws/projects/$', consumers.ProjectUpdateConsumer.as_asgi()),
]

