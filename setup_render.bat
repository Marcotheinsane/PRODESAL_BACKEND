@echo off
REM Script para preparar el deployment en Render
REM Ejecutar desde: cmd setup_render.bat

echo.
echo ===============================================================
echo        PREPARACION DE BACKEND PARA RENDER + NEON
echo ===============================================================
echo.

REM Verificar si python está disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python no encontrado en el PATH
    echo Por favor instala Python desde https://www.python.org
    pause
    exit /b 1
)

REM Verificar si pip está disponible
pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip no encontrado
    pause
    exit /b 1
)

echo [1/4] Instalando dependencias necesarias...
pip install psycopg python-dotenv

echo.
echo [2/4] Ejecutando script de migracion a Neon...
python migrate_to_neon.py
if errorlevel 1 (
    echo.
    echo Error: Fallo la migracion a Neon
    pause
    exit /b 1
)

echo.
echo [3/4] Generando configuracion de Render...
python setup_render.py

echo.
echo [4/4] Creando archivo .env...
if exist .env (
    echo Advertencia: .env ya existe
) else (
    copy .env.example .env
    echo .env creado desde .env.example
)

echo.
echo ===============================================================
echo   CONFIGURACION COMPLETADA
echo ===============================================================
echo.
echo Proximos pasos:
echo   1. Revisa el archivo render_env_config.txt
echo   2. Copia las variables al panel de Render
echo   3. Haz push a GitHub
echo   4. En Render crea un nuevo servicio Web
echo   5. Build: bash build.sh
echo   6. Start: gunicorn indapmuni.wsgi:application --bind 0.0.0.0:$PORT
echo.
echo Documentacion completa en: RENDER_DEPLOYMENT.md
echo.
pause
