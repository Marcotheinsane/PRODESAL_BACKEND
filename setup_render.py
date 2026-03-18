#!/usr/bin/env python
"""
Script para generar valores seguros y crear la configuración de Render
Uso: python setup_render.py
"""

import os
import secrets
import string
from pathlib import Path
from dotenv import load_dotenv

def generate_secret_key(length=50):
    """Genera una SECRET_KEY segura para Django"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
    return ''.join(secrets.choice(characters) for _ in range(length))

def print_section(title):
    """Imprime un título de sección"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def create_django_secret_key():
    """Crea una SECRET_KEY usando django"""
    try:
        from django.core.management.utils import get_random_secret_key
        return get_random_secret_key()
    except:
        return generate_secret_key()

def main():
    print_section("CONFIGURACIÓN DE RENDER PARA INDAPMUNI")
    
    # Generar SECRET_KEY
    print("Generando SECRET_KEY segura...")
    secret_key = create_django_secret_key()
    print(f"✓ SECRET_KEY generada")
    
    # URL de Neon
    neon_url = "postgresql://neondb_owner:npg_qZS1ue0yiBtU@ep-wispy-unit-ai3ueten-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    
    # Solicitar información del dominio frontend
    print("\n📋 INFORMACIÓN REQUERIDA EN RENDER:\n")
    
    frontend_url = input("URL del frontend en Render (ej: https://app.onrender.com): ").strip() or "http://localhost:5173"
    backend_url = input("URL del backend en Render (ej: https://api.onrender.com): ").strip() or "http://localhost:8000"
    
    # Crear archivo de configuración
    config_content = f"""
# VARIABLES DE ENTORNO PARA RENDER
# Copia y pega esto en el panel de Render

DEBUG=False
SECRET_KEY={secret_key}
DATABASE_URL={neon_url}

# Dominios
ALLOWED_HOSTS={backend_url.split('://')[-1]},localhost,127.0.0.1

# CORS - Frontend
CORS_ALLOWED_ORIGINS={frontend_url},http://localhost:5173,http://localhost:3000

# CSRF
CSRF_TRUSTED_ORIGINS={frontend_url},http://localhost:5173,http://localhost:3000
"""
    
    print_section("VARIABLES A CONFIGURAR EN RENDER")
    print(config_content)
    
    # Guardar en archivo
    render_config_file = Path('render_env_config.txt')
    with open(render_config_file, 'w') as f:
        f.write(config_content)
    
    print(f"\n✓ Configuración guardada en: {render_config_file}")
    
    # Instrucciones
    print_section("INSTRUCCIONES PARA RENDER")
    print("""
1. En el panel de Render:
   - Crea un nuevo servicio Web
   - Conecta tu repositorio Git
   - Build command: bash build.sh
   - Start command: gunicorn indapmuni.wsgi:application --bind 0.0.0.0:$PORT
   
2. Variables de entorno:
   - Copia las variables de render_env_config.txt al panel de Render
   - Environment Variables > Add Environment Variables
   
3. Base de datos:
   - La base de datos está en Neon (ya creada)
   - DATABASE_URL: Copia el valor de render_env_config.txt
   
4. Deploy:
   - Conecta tu repositorio
   - Render ejecutará build.sh automáticamente
   - Compila státicos y migra BD

5. Dominios CORS y CSRF:
   - Actualiza CORS_ALLOWED_ORIGINS con tu dominio frontend
   - Actualiza CSRF_TRUSTED_ORIGINS con tu dominio frontend
""")
    
    print("\n✓ CONFIGURACIÓN COMPLETADA")
    print(f"Guarda la configuración de: {render_config_file}")

if __name__ == '__main__':
    main()
