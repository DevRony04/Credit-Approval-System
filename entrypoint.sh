#!/usr/bin/env bash
set -e

python manage.py collectstatic --noinput || true
python manage.py makemigrations app --noinput || true
python manage.py migrate --noinput
python manage.py ingest_data || true

exec gunicorn credit_approval.asgi:application -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --workers 2
