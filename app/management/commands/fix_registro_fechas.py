import os
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
import openpyxl
from app.models import RegistroAsunto, Asunto


class Command(BaseCommand):
    help = 'Compara fechas de RegistroAsunto con el Excel original y corrige desvíos de ±1 día'

    def add_arguments(self, parser):
        parser.add_argument(
            '--excel',
            type=str,
            default='NOMINA 2025 CON SECTOR.xlsx',
            help='Ruta del archivo Excel original (default: NOMINA 2025 CON SECTOR.xlsx)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar cambios que se harían sin aplicarlos'
        )

    def handle(self, *args, **options):
        excel_path = options['excel']
        dry_run = options['dry_run']

        # Verificar que el archivo existe
        if not os.path.exists(excel_path):
            self.stdout.write(
                self.style.ERROR(f'Archivo no encontrado: {excel_path}')
            )
            return

        self.stdout.write(self.style.SUCCESS('=== Análisis de Fechas de RegistroAsunto ===\n'))

        # Cargar Excel
        try:
            wb = openpyxl.load_workbook(excel_path)
            ws = wb.active
            self.stdout.write(f'Excel cargado: {excel_path}')
            self.stdout.write(f'Hoja activa: {ws.title}\n')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al cargar Excel: {e}'))
            return

        # Extraer datos del Excel
        # Esperamos estructura: Nombre Asunto | Fecha | Lugar | Responsable (ajustar según sea necesario)
        excel_datos = {}  # {(asunto_nombre, fecha_excel): {lugar, responsable}}

        for row in ws.iter_rows(min_row=2, values_only=False):
            if row[0].value is None:  # Si la primera columna está vacía, saltamos
                continue

            nombre_asunto = row[0].value
            fecha_cell = row[1].value if len(row) > 1 else None
            lugar = row[2].value if len(row) > 2 else None
            responsable = row[3].value if len(row) > 3 else None

            # Si fecha_cell es None, saltamos
            if fecha_cell is None:
                continue

            # Convertir fecha a date si es datetime
            if hasattr(fecha_cell, 'date'):
                fecha = fecha_cell.date()
            elif isinstance(fecha_cell, str):
                try:
                    from datetime import datetime
                    fecha = datetime.strptime(fecha_cell, '%Y-%m-%d').date()
                except:
                    continue
            else:
                fecha = fecha_cell

            key = str(nombre_asunto)
            if key not in excel_datos:
                excel_datos[key] = []
            excel_datos[key].append({
                'fecha': fecha,
                'lugar': lugar,
                'responsable': responsable
            })

        self.stdout.write(f'Registros encontrados en Excel: {sum(len(v) for v in excel_datos.values())}\n')

        # Analizar RegistroAsunto en BD
        registros_bd = RegistroAsunto.objects.select_related('asunto').all()
        self.stdout.write(f'Registros en BD: {registros_bd.count()}\n')

        cambios = []
        sin_coincidencia = []
        sin_desvio = []
        count_corregidos = 0

        self.stdout.write('\n=== Comparando Fechas ===\n')

        for registro in registros_bd:
            asunto_nombre = str(registro.asunto.nombre)
            fecha_bd = registro.fecha.date() if hasattr(registro.fecha, 'date') else registro.fecha

            if asunto_nombre not in excel_datos:
                sin_coincidencia.append({
                    'asunto': asunto_nombre,
                    'fecha_bd': fecha_bd,
                    'razon': 'Asunto no encontrado en Excel'
                })
                continue

            # Buscar coincidencia de fecha en el Excel
            fechas_excel = [item['fecha'] for item in excel_datos[asunto_nombre]]
            
            # Verificar coincidencia exacta
            if fecha_bd in fechas_excel:
                sin_desvio.append({
                    'asunto': asunto_nombre,
                    'fecha': fecha_bd
                })
                continue

            # Buscar desvío de ±1 día
            fecha_correcta = None
            desvio = None

            if (fecha_bd + timedelta(days=1)) in fechas_excel:
                fecha_correcta = fecha_bd + timedelta(days=1)
                desvio = '+1'
            elif (fecha_bd - timedelta(days=1)) in fechas_excel:
                fecha_correcta = fecha_bd - timedelta(days=1)
                desvio = '-1'

            if fecha_correcta:
                cambios.append({
                    'registro_id': registro.id,
                    'asunto': asunto_nombre,
                    'fecha_actual': fecha_bd,
                    'fecha_correcta': fecha_correcta,
                    'desvio': desvio,
                    'lugar': registro.lugar,
                    'responsable': registro.responsable
                })
            else:
                sin_coincidencia.append({
                    'asunto': asunto_nombre,
                    'fecha_bd': fecha_bd,
                    'fechas_excel': fechas_excel[:3],
                    'razon': 'No hay coincidencia de ±1 día'
                })

        # Mostrar resultados
        self.stdout.write(self.style.SUCCESS(f'\n✓ Sin desvío (coincidencia exacta): {len(sin_desvio)}'))
        self.stdout.write(self.style.WARNING(f'⚠ Registros con desvío ±1: {len(cambios)}'))
        self.stdout.write(self.style.ERROR(f'✗ Sin coincidencia: {len(sin_coincidencia)}\n'))

        if cambios:
            self.stdout.write(self.style.WARNING('=== Cambios a Aplicar ===\n'))
            for i, cambio in enumerate(cambios, 1):
                print(f"{i}. {cambio['asunto'][:40]}")
                print(f"   Fecha actual: {cambio['fecha_actual']} → Fecha correcta: {cambio['fecha_correcta']} ({cambio['desvio']})")
                print()

        if sin_coincidencia and len(sin_coincidencia) <= 10:
            self.stdout.write(self.style.ERROR('=== Registros sin Coincidencia ===\n'))
            for item in sin_coincidencia[:10]:
                print(f"• {item['asunto'][:40]}: {item['fecha_bd']}")
                print(f"  Razón: {item.get('razon', 'Desconocida')}")
                if 'fechas_excel' in item:
                    print(f"  Fechas en Excel: {item['fechas_excel']}")
                print()

        # Aplicar cambios
        if cambios and not dry_run:
            self.stdout.write(self.style.WARNING('\n=== Aplicando Correcciones ===\n'))
            for cambio in cambios:
                try:
                    registro = RegistroAsunto.objects.get(id=cambio['registro_id'])
                    fecha_anterior = registro.fecha
                    registro.fecha = cambio['fecha_correcta']
                    registro.save()
                    count_corregidos += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ {cambio['asunto'][:40]}: {fecha_anterior.date()} → {cambio['fecha_correcta']}"
                        )
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"✗ Error corrigiendo {cambio['asunto']}: {e}"
                        )
                    )

            self.stdout.write(self.style.SUCCESS(f'\n\n=== Resumen ==='))
            self.stdout.write(self.style.SUCCESS(f'Total corregidos: {count_corregidos}'))

        elif dry_run and cambios:
            self.stdout.write(self.style.WARNING('\n(Modo --dry-run: No se aplicaron cambios)\n'))
        elif not cambios:
            self.stdout.write(self.style.SUCCESS('\n✓ No hay cambios necesarios. Todas las fechas coinciden.\n'))

        self.stdout.write(self.style.SUCCESS('✓ Análisis completado.\n'))
