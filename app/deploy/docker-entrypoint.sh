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

echo Create users
python manage.py createusers --noinput || true

celery -A config worker -l info -D
celery -A config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler --detach
uwsgi --ini /app/deploy/config.ini --daemonize /app/uwsgi.log
tail -f /app/uwsgi.log
