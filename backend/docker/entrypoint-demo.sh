#!/bin/sh
set -eu

python manage.py migrate --noinput
python manage.py seed_territories
if [ "${DJANGO_LOAD_DEMO_DATA:-false}" = "true" ]; then
  python manage.py seed_demo_instructors
fi
python manage.py collectstatic --noinput

exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers "${GUNICORN_WORKERS:-2}" \
  --threads "${GUNICORN_THREADS:-2}" \
  --timeout "${GUNICORN_TIMEOUT:-60}" \
  --access-logfile - \
  --error-logfile -
