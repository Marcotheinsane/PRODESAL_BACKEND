#!/usr/bin/env python
"""Crea archivo .env limpio con encoding UTF-8"""

import os

env_content = """DEBUG=False
SECRET_KEY=django-insecure-your-secret-key-here-change-in-production
DATABASE_URL=postgresql://neondb_owner:npg_qZS1ue0yiBtU@ep-wispy-unit-ai3ueten-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
ALLOWED_HOSTS=.onrender.com,localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://localhost:3000
"""

with open('.env', 'w', encoding='utf-8') as f:
    f.write(env_content)

print("✓ Archivo .env creado correctamente")
