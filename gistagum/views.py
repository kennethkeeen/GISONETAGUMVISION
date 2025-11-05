"""
Custom views for security and authentication
"""
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

@require_http_methods(["GET", "POST"])
@never_cache
def secure_logout(request):
    """
    Secure logout that clears all session data and prevents back button access
    """
    # Log the logout action
    if request.user.is_authenticated:
        logger.info(f"User {request.user.username} logged out")
    
    # Clear all session data
    request.session.flush()
    
    # Logout the user
    logout(request)
    
    # Add a message for the user
    messages.success(request, "You have been successfully logged out.")
    
    # Redirect to login page
    return redirect('login')

@login_required
@never_cache
def secure_home(request):
    """
    Secure home view with proper cache control
    """
    # This view ensures proper authentication and cache control
    return redirect('/admin/')  # Redirect to admin or your main dashboard

def redirect_to_login(request):
    """
    Redirect all root URL access to login page
    Always redirect to login, regardless of authentication status
    """
    # Force logout if user is already logged in to ensure fresh login
    if request.user.is_authenticated:
        from django.contrib.auth import logout
        logout(request)
        # Clear session data
        request.session.flush()
    
    return redirect('login')
