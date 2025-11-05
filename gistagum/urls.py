from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from accounts.views import dual_login, custom_logout
from gistagum.views import secure_logout, redirect_to_login
from monitoring import views as monitoring_views
from django.shortcuts import redirect
from projeng.views import engineer_projects_api
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__reload__/', include('django_browser_reload.urls')),
    path('logout/', secure_logout, name='logout'),
    path('accounts/login/', dual_login, name='login'),
    path('accounts/logout/', custom_logout, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/engineer-projects/<int:engineer_id>/', engineer_projects_api, name='engineer_projects_api'),
    path('projeng/', include(('projeng.urls', 'projeng'), namespace='projeng')),
    path('', redirect_to_login, name='home'),
    path('dashboard/', include('monitoring.urls')),
]

# This is only needed when running in development mode.
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 