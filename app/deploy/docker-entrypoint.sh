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

exec uwsgi --ini /app/deploy/config.ini
