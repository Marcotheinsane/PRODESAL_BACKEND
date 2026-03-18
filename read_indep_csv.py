#!/usr/bin/env python
import csv
from pathlib import Path

csv_path = r'c:\Users\Bimar\Desktop\Bd Muni\Nomina csv\indep.csv'

if not Path(csv_path).exists():
    print(f"Archivo no encontrado: {csv_path}")
    exit(1)

print(f"Leyendo: {csv_path}\n")

# Intentar diferentes codificaciones
encodings = ['latin-1', 'cp1252', 'iso-8859-1', 'utf-8']
success = False

for encoding in encodings:
    try:
        print(f"Intentando codificación: {encoding}...")
        
        with open(csv_path, 'r', encoding=encoding) as f:
            # Leer todas las líneas primero
            lines = f.readlines()
        
        # Ahora procesar con csv
        from io import StringIO
        csv_str = ''.join(lines)
        reader = csv.DictReader(StringIO(csv_str))
        
        rows = list(reader)
        print(f"✓ Éxito con codificación: {encoding}\n")
        
        if reader.fieldnames:
            print(f"Columnas encontradas: {list(reader.fieldnames)}\n")
        
        print("Primeras 10 filas:")
        print("-" * 120)
        
        for i, row in enumerate(rows[:10], 1):
            print(f"Fila {i}:")
            for key, val in list(row.items())[:10]:  # Primeras 10 columnas
                if val:
                    print(f"  {key:30} = {val}")
            print()
        
        print(f"Total de filas: {len(rows)}")
        success = True
        break
    except Exception as e:
        print(f"✗ Error con {encoding}: {e}\n")
        continue

if not success:
    print("Error: No se pudo leer el archivo con ninguna codificación")
