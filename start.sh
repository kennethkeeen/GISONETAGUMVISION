#!/bin/sh
# Startup script that detects if we should run as web service or worker

# Check if we should run as Celery worker
if [ -n "$CELERY_WORKER" ] || echo "$@" | grep -q "celery"; then
    echo "Starting as Celery worker..."
    # Worker doesn't need DATABASE_URL check (Celery will handle it)
    # But we still need it for Django settings
    if [ -z "$DATABASE_URL" ]; then
        echo "WARNING: DATABASE_URL not set, but continuing for worker..."
    fi
    exec "$@"
fi

# Otherwise, run as web service
echo "Starting application..."
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL environment variable is not set!"
    exit 1
fi

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn with optimized config..."
exec gunicorn gistagum.wsgi:application --config gunicorn_config.py

