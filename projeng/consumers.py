"""
WebSocket consumers for real-time updates (Phase 2: Parallel to SSE)
Handles notifications and project updates via WebSocket connections
"""

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from django.contrib.auth.models import AnonymousUser
from projeng.models import Notification, Project


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications
    Each user gets their own notification group
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        # Check if user is authenticated
        if self.scope["user"].is_anonymous:
            await self.close()
            return
        
        # Create user-specific group name
        self.group_name = f"user_{self.scope['user'].id}_notifications"
        
        # Join the user's notification group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        # Accept the WebSocket connection
        await self.accept()
        
        print(f"✅ WebSocket connected: User {self.scope['user'].username} - Group: {self.group_name}")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'group_name'):
            # Leave the user's notification group
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            print(f"✅ WebSocket disconnected: Group {self.group_name}")

    async def receive(self, text_data):
        """Handle messages received from WebSocket client"""
        try:
            data = json.loads(text_data)
            # For now, just echo back (can add custom handling later)
            await self.send(text_data=json.dumps({
                "type": "echo",
                "message": "Message received"
            }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Invalid JSON"
            }))

    async def send_notification(self, event):
        """Send notification to WebSocket client"""
        # This method is called when a notification is broadcast to this user's group
        await self.send(text_data=json.dumps(event["data"]))


class ProjectUpdateConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time project updates
    All users in the group receive project updates
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        # Check if user is authenticated
        if self.scope["user"].is_anonymous:
            await self.close()
            return
        
        # Check user permissions (Head Engineers, Project Engineers, Finance Managers)
        user = self.scope["user"]
        is_authorized = (
            user.is_superuser or
            user.groups.filter(name__in=['Head Engineer', 'Project Engineer', 'Finance Manager']).exists()
        )
        
        if not is_authorized:
            await self.close()
            return
        
        # Join the project updates group (shared by all authorized users)
        self.group_name = "project_updates"
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        # Accept the WebSocket connection
        await self.accept()
        
        print(f"✅ Project updates WebSocket connected: User {user.username}")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            print(f"✅ Project updates WebSocket disconnected")

    async def receive(self, text_data):
        """Handle messages received from WebSocket client"""
        try:
            data = json.loads(text_data)
            # For now, just echo back (can add custom handling later)
            await self.send(text_data=json.dumps({
                "type": "echo",
                "message": "Message received"
            }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Invalid JSON"
            }))

    async def send_update(self, event):
        """Send project update to WebSocket client"""
        # This method is called when a project update is broadcast
        await self.send(text_data=json.dumps(event["data"]))

