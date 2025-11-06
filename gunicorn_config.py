"""
Gunicorn configuration for optimal performance
"""
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
backlog = 2048

# Worker processes
# For small instances (1GB RAM), limit to 3 workers to prevent memory issues
# DigitalOcean 1vcpu-1gb instances should use max 3 workers
# Formula: (2 x CPU cores) + 1, but capped for small instances
cpu_count = multiprocessing.cpu_count()
calculated_workers = cpu_count * 2 + 1

# Limit workers for small instances (1GB RAM = max 3 workers)
# Check multiple ways DigitalOcean might indicate instance size
instance_size = os.environ.get('INSTANCE_SIZE', '')
instance_slug = os.environ.get('INSTANCE_SIZE_SLUG', '')
is_small_instance = (
    '1vcpu-1gb' in instance_size.lower() or 
    '1vcpu-1gb' in instance_slug.lower() or
    cpu_count == 1  # If only 1 CPU, it's likely a small instance
)

if is_small_instance:
    workers = min(calculated_workers, 3)
else:
    workers = int(os.environ.get('GUNICORN_WORKERS', calculated_workers))

# Use sync workers (threads not supported in sync, but we optimize workers instead)
# For I/O-bound operations, sync workers with proper worker count work well
# If you need threads, you'd use 'gthread' worker_class, but sync is simpler and works great
worker_class = 'sync'
# Note: Threads are not used with 'sync' worker_class
# For better concurrency, we optimize worker count instead

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

