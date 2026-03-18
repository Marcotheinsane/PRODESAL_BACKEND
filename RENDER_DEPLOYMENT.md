# Guía de Despliegue en Render + Neon PostgreSQL

## Descripción General

Este backend está configurado para desplegarse en [Render.com](https://render.com) con una base de datos PostgreSQL alojada en [Neon](https://neon.tech).

## Archivos de Configuración Nuevos

- `migrate_to_neon.py` - Script para migrar BD local a Neon
- `setup_render.py` - Script para generar configuración de Render
- `build.sh` - Script de construcción para Render
- `.env.example` - Plantilla de variables de entorno
- `requirements-render.txt` - Dependencias optimizadas para producción
- `render.yaml` - Configuración de infraestructura de Render

## Paso 1: Migrar Base de Datos a Neon

```bash
cd backend

# Instalar psycopg si no lo tienes
pip install psycopg

# Ejecutar migración
python migrate_to_neon.py
```

Este script:
1. ✓ Prueba conexión a BD local
2. ✓ Prueba conexión a Neon
3. ✓ Crea backup de BD local en `backups/`
4. ✓ Restaura datos a Neon
5. ✓ Verifica integridad de datos
6. ✓ Genera `.env.neon`

## Paso 2: Generar Configuración de Render

```bash
python setup_render.py
```

Este script:
1. ✓ Genera `SECRET_KEY` segura
2. ✓ Crea `render_env_config.txt` con todas las variables
3. ✓ Guía configuración paso a paso

## Paso 3: Crear Servicio en Render

1. Ve a [render.com](https://render.com)
2. Crea una cuenta / inicia sesión
3. Crea un nuevo servicio Web:
   - **Repository**: Conecta tu repo de GitHub
   - **Build Command**: `bash build.sh`
   - **Start Command**: `gunicorn indapmuni.wsgi:application --bind 0.0.0.0:$PORT`
   - **Environment**: Python 3.11

## Paso 4: Configurar Variables de Entorno

En el panel de Render, ve a **Environment**:

Copia las variables de `render_env_config.txt`:

```
DEBUG=False
SECRET_KEY=<generado>
DATABASE_URL=postgresql://neondb_owner:npg_qZS1ue0yiBtU@...
ALLOWED_HOSTS=.onrender.com,localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=https://tu-frontend.onrender.com,http://localhost:5173
CSRF_TRUSTED_ORIGINS=https://tu-frontend.onrender.com,http://localhost:5173
```

## Paso 5: Deploy

1. Conecta tu repositorio a Render
2. Render ejecutará automáticamente `build.sh`:
   - Instala dependencias
   - Ejecuta migraciones Django
   - Compila archivos estáticos con WhiteNoise

## Base de Datos Neon

**Conexión Neon (Ya configurada):**
```
postgresql://neondb_owner:npg_qZS1ue0yiBtU@ep-wispy-unit-ai3ueten-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

### Características:
- ✓ Base de datos PostgreSQL fully managed
- ✓ SSL/TLS automatizado
- ✓ Backups automáticos
- ✓ Escalado automático

## Cambios Realizados en el Código

### `settings.py`
- ✓ Agregado soporte para `DATABASE_URL` con `dj-database-url`
- ✓ Agregado `WhiteNoise` para servir archivos estáticos
- ✓ Configuración de seguridad para HTTPS en producción
- ✓ CORS y CSRF ajustados para múltiples dominios
- ✓ Support para Render.com

### `build.sh`
Nuevo script que ejecuta Render durante el build:
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --no-input
```

### Middleware
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← NUEVO
    ...
]
```

### Static Files
```python
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

## Troubleshooting

### Error: "No module named 'dj_database_url'"
**Solución:** Asegúrate de tener `requirements.txt` actualizado:
```bash
pip install dj-database-url
```

### Error: "psql: command not found"
**Solución:** Debes tener PostgreSQL instalado en tu máquina local para el script de migración.
- Windows: [postgresql.org Downloads](https://www.postgresql.org/download/windows/)
- macOS: `brew install postgresql@15`
- Linux: `sudo apt-get install postgresql`

### Error: "FATAL: password authentication failed"
**Solución:** Verifica las credenciales en `.env`:
```
DB_HOST=127.0.0.1
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=tu_contraseña
```

### Error: "SSL certificate verification failed"
**Solución:** En Windows, descarga `libpq`:
```bash
pip install psycopg[binary]
```

### Static Files no se sirven en Render
**Solución:** Ejecuta manualmente después de deploy:
```bash
python manage.py collectstatic --no-input
```

## Variables de Entorno Críticas

| Variable | Ejemplo | Descripción |
|----------|---------|-------------|
| `DEBUG` | `False` | NUNCA `True` en producción |
| `SECRET_KEY` | `django-insecure-...` | Generada con `django.core.management.utils.get_random_secret_key()` |
| `DATABASE_URL` | `postgresql://...` | URL de conexión Neon |
| `ALLOWED_HOSTS` | `.onrender.com,localhost` | Dominios permitidos |
| `CORS_ALLOWED_ORIGINS` | `https://app.onrender.com` | Dominios frontend |
| `CSRF_TRUSTED_ORIGINS` | `https://app.onrender.com` | Dominios CSRF |

## Monitoring en Render

1. **Logs**: Panel de Render > Logs
2. **Métricas**: Panel de Render > Metrics
3. **Web Requests**: Panel de Render > View Recent Requests

## Rollback / Recuperación

Si algo sale mal:

1. En Render, puedes revertir a un deploy anterior
2. El backup local está en `backups/backup_*.sql`
3. Para recuperar localmente:
   ```bash
   psql -U postgres -d indapmuni -f backups/backup_YYYYMMDD_HHMMSS.sql
   ```

## Próximos Pasos

1. ✓ Ejecuta `python migrate_to_neon.py`
2. ✓ Ejecuta `python setup_render.py`
3. ✓ Sube a GitHub
4. ✓ Crea servicio en Render
5. ✓ Configura variables de entorno
6. ✓ Deploy automático

¡Tu backend estará vivo en minutos! 🚀
