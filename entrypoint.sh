#!/bin/bash
set -e

echo "==> Esperando a que la base de datos esté lista..."
until python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()
from django.db import connection
connection.ensure_connection()
print('DB lista')
" 2>/dev/null; do
  echo "   DB no disponible, reintentando en 2s..."
  sleep 2
done

echo "==> Aplicando migraciones..."
python manage.py migrate --noinput

echo "==> Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

echo "==> Compilando traducciones..."
python manage.py compilemessages --ignore=. 2>/dev/null || true

echo "==> Arrancando gunicorn..."
exec gunicorn project.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
