import random
from django.core.management.base import BaseCommand
from django.db.models import Count
from app.models import Asistencia, RegistroAsunto, Asunto, Clientes
from datetime import datetime


class Command(BaseCommand):
    help = 'Genera asistencias realistas basadas en patrones de PRODESAL Valdivia 2025'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Eliminar asistencias dañadas del 9-10 de febrero antes de generar nuevas',
        )

    def obtener_tipo_evento(self, nombre_asunto):
        """Clasificar evento por tipo"""
        nombre_lower = nombre_asunto.lower()
        
        if any(w in nombre_lower for w in ['entrega', 'semilla']):
            return 'entrega'
        elif any(w in nombre_lower for w in ['inicio de temporada']):
            return 'reunion_inicio'
        elif any(w in nombre_lower for w in ['mercado']):
            return 'mercado'
        elif any(w in nombre_lower for w in ['taller', 'capacitacion']):
            return 'taller'
        elif any(w in nombre_lower for w in ['charla']):
            return 'charla'
        elif any(w in nombre_lower for w in ['gira', 'visita']):
            return 'gira'
        else:
            return 'reunion'

    def obtener_rango_asistentes(self, tipo_evento, num_registrados):
        """Definir rango de asistentes según tipo de evento"""
        ranges = {
            'entrega': (35, 40),           # Entregas de semillas: 37-40
            'reunion_inicio': (20, 40),    # Reuniones inicio año: pueden tener más
            'mercado': (30, 40),           # Mercados campesinos: 30-40
            'taller': (12, 27),            # Talleres: 15-27
            'charla': (8, 18),             # Charlas: 8-18
            'gira': (8, 20),               # Giras: 8-20
            'reunion': (10, 25),           # Reuniones generales: 10-25
        }
        
        min_asist, max_asist = ranges.get(tipo_evento, (4, 15))
        
        # No más de lo que hay registrado
        max_asist = min(max_asist, num_registrados)
        min_asist = min(min_asist, num_registrados)
        
        return min_asist, max_asist

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 80))
        self.stdout.write(self.style.SUCCESS('GENERANDO ASISTENCIAS REALISTAS'))
        self.stdout.write(self.style.SUCCESS('=' * 80 + '\n'))

        # 1. LIMPIAR DATOS DAÑADOS SI SE SOLICITA
        if options['limpiar']:
            self.stdout.write('🗑️  Limpiando asistencias dañadas del 9-10 de febrero...')
            
            # Asistencias del 9 de febrero
            asist_9feb_count = Asistencia.objects.filter(
                fecha_registro__date='2025-02-09'
            ).count()
            
            # Asistencias del 10 de febrero - obtener IDs para eliminar
            asist_10feb_ids = list(
                Asistencia.objects.filter(
                    fecha_registro__date='2025-02-10'
                ).order_by('-fecha_registro').values_list('id', flat=True)[57:]
            )
            
            total_a_eliminar = asist_9feb_count + len(asist_10feb_ids)
            
            Asistencia.objects.filter(
                fecha_registro__date='2025-02-09'
            ).delete()
            
            Asistencia.objects.filter(id__in=asist_10feb_ids).delete()
            
            self.stdout.write(f'  ✓ Eliminadas {total_a_eliminar} asistencias dañadas\n')

        # 2. ANÁLISIS DE ASUNTOS Y CLIENTES REGISTRADOS
        self.stdout.write('📊 Fase 1: Analizando estructura de datos...')

        asuntos_data = Asunto.objects.annotate(
            num_clientes=Count('asistentes', distinct=True),
            num_instancias=Count('registros')
        ).filter(num_clientes__gt=0)

        self.stdout.write(f'  ✓ {asuntos_data.count()} asuntos con clientes registrados')

        # 3. OBTENER CLIENTES CON MAYOR PARTICIPACIÓN
        self.stdout.write('\n🌟 Fase 2: Identificando personas más activas...')

        clientes_activos = Clientes.objects.annotate(
            num_asuntos=Count('asuntos_asociados', distinct=True)
        ).filter(num_asuntos__gt=0).order_by('-num_asuntos')

        self.stdout.write(f'  ✓ {clientes_activos.count()} personas registradas en asuntos')

        top_clientes = list(clientes_activos[:50])  # Top 50 más activos
        self.stdout.write(f'  ✓ Usando top {len(top_clientes)} personas como base')

        # 4. GENERAR ASISTENCIAS COHERENTES
        self.stdout.write('\n💾 Fase 3: Generando asistencias realistas...')

        nuevas_asistencias = []
        eventos_procesados = 0
        asistencias_creadas = 0
        asistencias_saltadas = 0

        for asunto in asuntos_data:
            tipo = self.obtener_tipo_evento(asunto.nombre)
            clientes_registrados = list(asunto.asistentes.all())
            
            if not clientes_registrados:
                continue

            # Para cada registro (instancia) del asunto
            for registro in asunto.registros.all():
                # Verificar si ya hay asistencias
                ya_tiene = Asistencia.objects.filter(
                    registro_asunto=registro
                ).exists()
                
                if ya_tiene:
                    asistencias_saltadas += 1
                    continue

                # Determinar cantidad de asistentes
                min_asist, max_asist = self.obtener_rango_asistentes(
                    tipo, len(clientes_registrados)
                )
                cantidad_asistentes = random.randint(min_asist, max_asist)
                cantidad_asistentes = min(cantidad_asistentes, len(clientes_registrados))

                # Seleccionar clientes: priorizar a los más activos
                clientes_top_asunto = [
                    c for c in top_clientes if c in clientes_registrados
                ]
                clientes_otros = [
                    c for c in clientes_registrados if c not in top_clientes
                ]

                # Mezclar: 70% top activos, 30% otros
                proporcion_top = int(cantidad_asistentes * 0.7)
                proporcion_otros = cantidad_asistentes - proporcion_top

                clientes_seleccionados = []
                
                if clientes_top_asunto:
                    clientes_seleccionados.extend(
                        random.sample(
                            clientes_top_asunto,
                            min(proporcion_top, len(clientes_top_asunto))
                        )
                    )
                
                if clientes_otros and len(clientes_seleccionados) < cantidad_asistentes:
                    clientes_seleccionados.extend(
                        random.sample(
                            clientes_otros,
                            min(
                                proporcion_otros,
                                len(clientes_otros),
                                cantidad_asistentes - len(clientes_seleccionados)
                            )
                        )
                    )

                # Crear registros de asistencia con variabilidad
                for cliente in clientes_seleccionados:
                    # 85% asisten, 15% faltan (variabilidad realista)
                    presente = random.random() < 0.85
                    
                    asistencia = Asistencia(
                        cliente=cliente,
                        registro_asunto=registro,
                        presente=presente
                    )
                    nuevas_asistencias.append(asistencia)
                    asistencias_creadas += 1

                eventos_procesados += 1

        # 5. GUARDAR EN LOTE
        if nuevas_asistencias:
            Asistencia.objects.bulk_create(nuevas_asistencias, batch_size=1000)
            self.stdout.write(f'  ✓ Asistencias creadas: {asistencias_creadas}')
            self.stdout.write(f'  ✓ Eventos procesados: {eventos_procesados}')

        # 6. ESTADÍSTICAS FINALES
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write('📊 ESTADÍSTICAS FINALES:')
        self.stdout.write('=' * 80)

        total_asistencias = Asistencia.objects.count()
        clientes_con_asist = Asistencia.objects.values_list(
            'cliente_id', flat=True
        ).distinct().count()
        registros_con_asist = Asistencia.objects.values_list(
            'registro_asunto_id', flat=True
        ).distinct().count()

        presentes = Asistencia.objects.filter(presente=True).count()
        ausentes = Asistencia.objects.filter(presente=False).count()
        tasa_asist = (presentes / total_asistencias * 100) if total_asistencias > 0 else 0

        self.stdout.write(f'  ✓ Total asistencias: {total_asistencias}')
        self.stdout.write(f'  ✓ Clientes únicos: {clientes_con_asist}')
        self.stdout.write(f'  ✓ Registros con asistencia: {registros_con_asist}')
        self.stdout.write(f'  ✓ Promedio por evento: {total_asistencias / max(1, registros_con_asist):.1f}')
        self.stdout.write(f'  ✓ Presentes: {presentes} ({tasa_asist:.1f}%)')
        self.stdout.write(f'  ✓ Ausentes: {ausentes} ({100-tasa_asist:.1f}%)')

        # Mostrar distribución por tipo (simplificado)
        self.stdout.write('\n📈 Resumen: Datos generados correctamente')
        self.stdout.write('   - Entregas: 37-40 asistentes')
        self.stdout.write('   - Reuniones inicio año: 20-40 asistentes')
        self.stdout.write('   - Mercados: 30-40 asistentes')
        self.stdout.write('   - Talleres: 12-27 asistentes')
        self.stdout.write('   - Charlas: 8-18 asistentes')

        self.stdout.write(self.style.SUCCESS('\n✅ Generación completada.\n'))
