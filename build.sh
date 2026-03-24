#!/bin/bash
set -e

echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🗄️ Aplicando migraciones..."
python manage.py migrate --noinput

echo "📁 Recopilando estáticos..."
python manage.py collectstatic --noinput --clear

echo "✅ Build completado"

