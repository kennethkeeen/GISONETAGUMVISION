"""
WebSocket broadcasting utilities (Phase 3: Parallel to SSE)
Helper functions to send updates via WebSocket alongside SSE
"""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from projeng.models import Notification


def broadcast_notification(user_id, notification_data):
    """
    Broadcast notification via WebSocket to a specific user (parallel to SSE)
    
    Args:
        user_id: ID of the user to notify
        notification_data: Dictionary containing notification data
    """
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"user_{user_id}_notifications",
                {
                    "type": "send_notification",
                    "data": notification_data
                }
            )
            print(f"✅ WebSocket notification broadcast to user_{user_id}")
    except Exception as e:
        # Fail silently - SSE is still working
        # This ensures WebSocket failures don't break the system
        print(f"⚠️  WebSocket broadcast failed (SSE still works): {e}")


def broadcast_notification_to_user(user, message, notification_id=None):
    """
    Convenience function to broadcast notification to a user
    
    Args:
        user: User instance to notify
        message: Notification message
        notification_id: Optional notification ID
    """
    notification_data = {
        'type': 'notification',
        'message': message,
        'notification_id': notification_id,
    }
    broadcast_notification(user.id, notification_data)


def broadcast_project_update(update_data):
    """
    Broadcast project update via WebSocket to all authorized users (parallel to SSE)
    
    Args:
        update_data: Dictionary containing project update data
    """
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                "project_updates",
                {
                    "type": "send_update",
                    "data": update_data
                }
            )
            print(f"✅ WebSocket project update broadcast: {update_data.get('type', 'unknown')}")
    except Exception as e:
        # Fail silently - SSE is still working
        print(f"⚠️  WebSocket broadcast failed (SSE still works): {e}")


def broadcast_project_created(project):
    """
    Broadcast when a new project is created
    
    Args:
        project: Project instance
    """
    broadcast_project_update({
        'type': 'project_created',
        'project_id': project.id,
        'name': project.name,
        'prn': project.prn,
        'status': project.status,
        'barangay': project.barangay,
    })


def broadcast_project_updated(project, changes=None):
    """
    Broadcast when a project is updated
    
    Args:
        project: Project instance
        changes: Optional dictionary of what changed
    """
    update_data = {
        'type': 'project_updated',
        'project_id': project.id,
        'name': project.name,
        'prn': project.prn,
        'status': project.status,
        'barangay': project.barangay,
    }
    if changes:
        update_data['changes'] = changes
    
    broadcast_project_update(update_data)


def broadcast_project_deleted(project_name, project_prn=None):
    """
    Broadcast when a project is deleted
    
    Args:
        project_name: Name of the deleted project
        project_prn: Optional PRN of the deleted project
    """
    broadcast_project_update({
        'type': 'project_deleted',
        'name': project_name,
        'prn': project_prn,
    })


def broadcast_project_status_change(project, old_status, new_status):
    """
    Broadcast when project status changes
    
    Args:
        project: Project instance
        old_status: Previous status
        new_status: New status
    """
    broadcast_project_update({
        'type': 'project_status_changed',
        'project_id': project.id,
        'name': project.name,
        'prn': project.prn,
        'old_status': old_status,
        'new_status': new_status,
    })


def broadcast_cost_update(project, cost_data):
    """
    Broadcast when a cost entry is added/updated
    
    Args:
        project: Project instance
        cost_data: Dictionary with cost information
    """
    broadcast_project_update({
        'type': 'cost_updated',
        'project_id': project.id,
        'project_name': project.name,
        'cost_data': cost_data,
    })


def broadcast_progress_update(project, progress_data):
    """
    Broadcast when project progress is updated
    
    Args:
        project: Project instance
        progress_data: Dictionary with progress information
    """
    broadcast_project_update({
        'type': 'progress_updated',
        'project_id': project.id,
        'project_name': project.name,
        'progress_data': progress_data,
    })

