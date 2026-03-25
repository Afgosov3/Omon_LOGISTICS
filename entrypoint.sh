#!/bin/sh
set -e

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Creating default dispatchers..."
python manage.py create_default_dispatchers || true

echo "Starting Gunicorn..."
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4