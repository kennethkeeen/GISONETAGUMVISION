"""
Gunicorn configuration for optimal performance
"""
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
backlog = 2048

# Worker processes
# Formula: (2 x CPU cores) + 1
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
# Limit workers for small instances (1GB RAM = max 3 workers)
if os.environ.get('INSTANCE_SIZE', '').startswith('apps-s-1vcpu'):
    workers = min(workers, 3)

worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
loglevel = os.environ.get('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'gistagum'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_redirect = False

# Worker recycling (prevents memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Preload app for better performance
preload_app = True

# Worker timeout
graceful_timeout = 30

