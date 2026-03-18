import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from app.models import Asunto, RegistroAsunto


# Mapa de meses en español a número
MESES_ESPAÑOL = {
    'janeiro': 1, 'enero': 1,
    'fevereiro': 2, 'febrero': 2,
    'março': 3, 'marzo': 3,
    'abrit': 4, 'abril': 4,
    'maio': 5, 'mayo': 5,
    'junho': 6, 'junio': 6,
    'julho': 7, 'julio': 7,
    'agosto': 8,
    'setembro': 9, 'setiembre': 9, 'septiembre': 9,
    'outubro': 10, 'octubr': 10, 'octubre': 10,
    'novembro': 11, 'noviembre': 11,
    'dezembro': 12, 'diciembre': 12
}


def parse_fecha_spanish(fecha_str):
    """Parse fecha en formato español como '19 de Noviembre 2025'"""
    if not fecha_str or fecha_str.lower() in ['n/a', 'na', '']:
        return None
    
    try:
        # Limpiar espacios
        fecha_str = fecha_str.strip()
        
        # Formato: "19 de Noviembre 2025"
        partes = fecha_str.lower().split()
        
        if len(partes) < 3:
            return None
        
        dia = int(partes[0])
        # partes[1] debería ser "de"
        mes_str = partes[2]
        anio = int(partes[3]) if len(partes) > 3 else datetime.now().year
        
        # Encontrar el mes
        mes = None
        for mes_name, mes_num in MESES_ESPAÑOL.items():
            if mes_str.startswith(mes_name[:3]):  # Comparar primeros 3 caracteres
                mes = mes_num
                break
        
        if mes is None:
            # Intentar buscar parcialmente
            for mes_name, mes_num in MESES_ESPAÑOL.items():
                if mes_name in mes_str:
                    mes = mes_num
                    break
        
        if mes is None:
            return None
        
        # Crear fecha
        fecha = datetime(anio, mes, dia).date()
        return fecha
    
    except Exception as e:
        return None


class Command(BaseCommand):
    help = 'Importa asuntos y registros desde indep.csv con fechas correctas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            default=r'c:\Users\Bimar\Desktop\Bd Muni\Nomina csv\indep.csv',
            help='Ruta del archivo CSV'
        )

    def handle(self, *args, **options):
        csv_path = options['csv']
        
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f'Archivo no encontrado: {csv_path}'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'\n=== Cargando datos desde {csv_path} ===\n'))
        
        registros_importados = 0
        registros_actualizados = 0
        errores = 0
        
        try:
            with open(csv_path, 'r', encoding='latin-1') as f:
                # Usar delimiter ; y manejar correctamente el CSV
                reader = csv.DictReader(f, delimiter=';', fieldnames=['asunto', 'fecha', 'lugar', 'responsable'])
                
                # Saltar encabezado si existe
                next(reader, None)
                
                print(f"{'N°':3} | {'Asunto':40} | {'Fecha':20} | {'Estado':20}\n")
                print("-" * 95)
                
                for i, row in enumerate(reader, 1):
                    try:
                        asunto_nombre = row['asunto'].strip() if row['asunto'] else None
                        fecha_str = row['fecha'].strip() if row['fecha'] else None
                        lugar = row['lugar'].strip() if row['lugar'] else None
                        responsable = row['responsable'].strip() if row['responsable'] else None
                        
                        if not asunto_nombre or not fecha_str:
                            continue
                        
                        # Parsear fecha
                        fecha = parse_fecha_spanish(fecha_str)
                        if not fecha:
                            print(f"{i:3} | {asunto_nombre[:38]:38} | {fecha_str[:18]:18} | ✗ Fecha no parseada")
                            errores += 1
                            continue
                        
                        # Buscar o crear asunto
                        asunto, created = Asunto.objects.get_or_create(nombre=asunto_nombre)
                        
                        # Buscar o crear registro
                        registro, created = RegistroAsunto.objects.get_or_create(
                            asunto=asunto,
                            fecha=fecha,
                            defaults={
                                'lugar': lugar if lugar and lugar.lower() not in ['n/a', 'na'] else '',
                                'responsable': responsable if responsable and responsable.lower() not in ['n/a', 'na'] else '',
                            }
                        )
                        
                        if created:
                            estado = "✓ Nuevo"
                            registros_importados += 1
                        else:
                            # Actualizar si ya existe
                            if lugar and lugar.lower() not in ['n/a', 'na']:
                                registro.lugar = lugar
                            if responsable and responsable.lower() not in ['n/a', 'na']:
                                registro.responsable = responsable
                            
                            registro.save()
                            estado = "◆ Actualizado"
                            registros_actualizados += 1
                        
                        print(f"{i:3} | {asunto_nombre[:38]:38} | {str(fecha):18} | {estado}")
                    
                    except Exception as e:
                        print(f"{i:3} | {'ERROR':38} | {str(e)[:18]:18} | ✗ Excepción")
                        errores += 1
                        continue
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error leyendo archivo: {e}'))
            return
        
        self.stdout.write(f"\n{'-' * 95}\n")
        self.stdout.write(self.style.SUCCESS(f'✓ Nuevos registros: {registros_importados}'))
        self.stdout.write(self.style.WARNING(f'◆ Registros actualizados: {registros_actualizados}'))
        self.stdout.write(self.style.ERROR(f'✗ Errores: {errores}'))
        self.stdout.write(self.style.SUCCESS(f'\n✓ Importación completada.\n'))
