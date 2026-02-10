#!/bin/bash
set -e

echo "Creating media directories..."
mkdir -p /app/media/products/gallery /app/media/products/content /app/media/banners /app/media/popups

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Starting Gunicorn..."
exec gunicorn atelier.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120
