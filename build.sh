#!/bin/bash
# build.sh - Script de construcción para Render

set -o errexit

echo "Instalando dependencias..."
pip install -r requirements.txt

echo "Migrando base de datos..."
python manage.py migrate

echo "Recopilando archivos estáticos..."
python manage.py collectstatic --no-input

echo "✓ Build completado"

# Iniciar gunicorn
echo "Iniciando servidor..."
exec python -m gunicorn indapmuni.wsgi:application --bind 0.0.0.0:${PORT:-8000}
