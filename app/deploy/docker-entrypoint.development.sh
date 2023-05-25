#!/usr/bin/env bash
set -u   # crash on missing env variables
set -e   # stop on any error
set -x

echo Apply migrations
python manage.py migrate --noinput

echo Collecting static files
python manage.py collectstatic --no-input

echo Create superuser
python manage.py createsuperuser --noinput || true

exec python -m debugpy --listen 0.0.0.0:5678 /app/manage.py runserver 0.0.0.0:8000
