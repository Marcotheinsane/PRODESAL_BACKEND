#!/usr/bin/env python
"""
Script para analizar y corregir fechas de RegistroAsunto
Uso: python fix_dates_helper.py [--apply]
  - Sin --apply: muestra cambios necesarios (dry-run)
  - Con --apply: aplica las correcciones
"""

import os
import sys
import subprocess

def main():
    # Verificar que estemos en el directorio correcto
    if not os.path.exists('manage.py'):
        print("Error: Este script debe ejecutarse desde el directorio raíz del proyecto")
        print("Directorio actual:", os.getcwd())
        sys.exit(1)

    # Verificar que el Excel existe
    excel_file = 'NOMINA 2025 CON SECTOR.xlsx'
    if not os.path.exists(excel_file):
        print(f"Error: No se encontró {excel_file}")
        sys.exit(1)

    apply_changes = '--apply' in sys.argv

    if apply_changes:
        print("\n" + "="*70)
        print("MODO: APLICAR CAMBIOS")
        print("="*70 + "\n")
        cmd = ['python', 'manage.py', 'fix_registro_fechas', '--excel', excel_file]
    else:
        print("\n" + "="*70)
        print("MODO: ANÁLISIS SOLAMENTE (Dry-Run)")
        print("Para aplicar cambios, ejecuta: python fix_dates_helper.py --apply")
        print("="*70 + "\n")
        cmd = ['python', 'manage.py', 'fix_registro_fechas', '--excel', excel_file, '--dry-run']

    # Ejecutar el comando
    try:
        result = subprocess.run(cmd, check=False)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Error ejecutando comando: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
