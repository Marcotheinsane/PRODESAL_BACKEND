#!/usr/bin/env python
"""
Script para migrar la base de datos local a Neon PostgreSQL
Uso: python migrate_to_neon.py
"""

import os
import sys
import subprocess
import psycopg
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Configuración
LOCAL_DB = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'port': os.getenv('DB_PORT', '5433'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '2077'),
    'database': os.getenv('DB_NAME', 'indapmuni'),
}

NEON_URL = os.getenv('NEON_DATABASE_URL', 'postgresql://neondb_owner:npg_qZS1ue0yiBtU@ep-wispy-unit-ai3ueten-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require')

BACKUP_DIR = Path('backups')
BACKUP_DIR.mkdir(exist_ok=True)

def print_header(msg):
    """Imprime un mensaje de encabezado"""
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}\n")

def create_local_backup():
    """Crea un backup de la BD local"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = BACKUP_DIR / f'backup_{timestamp}.sql'
    
    print_header(f"Creando backup local en {backup_file}")
    
    try:
        cmd = [
            'pg_dump',
            '-h', LOCAL_DB['host'],
            '-p', LOCAL_DB['port'],
            '-U', LOCAL_DB['user'],
            '-d', LOCAL_DB['database'],
            '-F', 'plain',  # Formato texto para facilitar
            '--no-owner',   # No incluir propietarios
            '--no-privileges',  # No incluir permisos
            '-f', str(backup_file)
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = LOCAL_DB['password']
        
        result = subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
        print(f"✓ Backup creado exitosamente: {backup_file}")
        print(f"  Tamaño: {backup_file.stat().st_size / (1024*1024):.2f} MB")
        return backup_file
    except subprocess.CalledProcessError as e:
        print(f"✗ Error creando backup: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("✗ Error: pg_dump no encontrado. Asegúrate de que PostgreSQL esté instalado.")
        sys.exit(1)

def test_local_connection():
    """Prueba la conexión a la BD local"""
    print_header("Probando conexión a BD local")
    
    try:
        conn = psycopg.connect(
            host=LOCAL_DB['host'],
            port=LOCAL_DB['port'],
            user=LOCAL_DB['user'],
            password=LOCAL_DB['password'],
            dbname=LOCAL_DB['database']
        )
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        result = cursor.fetchone()
        print(f"✓ Conectado a BD local: {result[0].split(',')[0]}")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"✗ Error conectando a BD local: {e}")
        print("\nVerifica que PostgreSQL esté corriendo y que las credenciales sean correctas.")
        sys.exit(1)

def test_neon_connection():
    """Prueba la conexión a Neon"""
    print_header("Probando conexión a Neon")
    
    try:
        conn = psycopg.connect(NEON_URL)
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        result = cursor.fetchone()
        print(f"✓ Conectado a Neon: {result[0].split(',')[0]}")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"✗ Error conectando a Neon: {e}")
        print("\nVerifica que la URL DATABASE_URL sea correcta.")
        sys.exit(1)

def restore_to_neon(backup_file):
    """Restaura el backup a Neon"""
    print_header(f"Restaurando datos a Neon desde {backup_file.name}")
    
    try:
        with open(backup_file, 'r') as f:
            # Limpiar la BD Neon primero
            print("Limpiando BD destino...")
            conn = psycopg.connect(NEON_URL)
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Eliminar todas las tablas
            cursor.execute("""
                DO $$ DECLARE
                    r RECORD;
                BEGIN
                    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                    END LOOP;
                END $$;
            """)
            cursor.close()
            conn.close()
            print("✓ BD destino limpiada")
            
            # Restaurar datos ignorando errores de roles/propietarios
            print("Restaurando datos...")
            cmd = [
                'psql',
                NEON_URL,
                '-f', str(backup_file),
                '--set', 'ON_ERROR_STOP=off'  # Continuar a pesar de errores de roles
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Verificar si hubo errores críticos (no son solo de roles)
            if 'error' in result.stderr.lower() and 'role' not in result.stderr.lower():
                print(f"✗ Error restaurando datos: {result.stderr}")
                return False
            
            print("✓ Datos restaurados exitosamente a Neon")
            return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error restaurando datos: {e.stderr}")
        return False
    except FileNotFoundError:
        print("✗ Error: psql no encontrado. Asegúrate de que PostgreSQL esté instalado.")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def verify_neon():
    """Verifica que los datos estén en Neon"""
    print_header("Verificando datos en Neon")
    
    try:
        conn = psycopg.connect(NEON_URL)
        cursor = conn.cursor()
        
        # Contar tablas
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
        table_count = cursor.fetchone()[0]
        print(f"✓ Tablas en Neon: {table_count}")
        
        # Listar tablas
        cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;")
        tables = cursor.fetchall()
        
        total_records = 0
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
                row_count = cursor.fetchone()[0]
                total_records += row_count
                print(f"  - {table[0]}: {row_count} registros")
            except Exception as e:
                print(f"  - {table[0]}: [error consultando]")
        
        print(f"\n✓ Total de registros: {total_records}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Error verificando: {e}")
        return False

def create_env_file():
    """Crea archivo .env con la configuración de Neon"""
    print_header("Creando archivo .env.neon")
    
    env_content = f"""# Configuración para Neon PostgreSQL
DEBUG=False
SECRET_KEY={os.getenv('SECRET_KEY', 'django-insecure-change-me-in-production')}
DATABASE_URL={NEON_URL}
ALLOWED_HOSTS=.onrender.com,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://*.onrender.com,http://localhost
"""
    
    env_file = Path('.env.neon')
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✓ Archivo creado: {env_file}")
    print(f"  Usa: copy .env.neon .env (en Windows) o cp .env.neon .env (en Linux/Mac)")

def main():
    """Función principal"""
    print_header("MIGRACIÓN DE BD LOCAL A NEON POSTGRESQL")
    
    # Paso 1: Probar conexiones
    test_local_connection()
    test_neon_connection()
    
    # Paso 2: Crear backup
    backup_file = create_local_backup()
    
    # Paso 3: Restaurar a Neon
    if not restore_to_neon(backup_file):
        print("\n✗ La migración falló. Verifica los errores arriba.")
        sys.exit(1)
    
    # Paso 4: Verificar
    verify_neon()
    
    # Paso 5: Crear archivo .env
    create_env_file()
    
    print_header("✓ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("\nPróximos pasos:")
    print("1. Reemplaza el archivo .env con .env.neon")
    print("2. Ejecuta: python manage.py migrate")
    print("3. En Render, establece la variable DATABASE_URL")

if __name__ == '__main__':
    main()
