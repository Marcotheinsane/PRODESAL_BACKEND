import random
from django.core.management.base import BaseCommand
from django.db.models import Count
from app.models import Asistencia, RegistroAsunto, Asunto, Clientes


class Command(BaseCommand):
    help = 'Genera asistencias realistas con patrones de PRODESAL Valdivia'

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
            'entrega': (35, 40),           # Entregas: 37-40
            'reunion_inicio': (25, 40),    # Reuniones inicio: pueden tener más
            'mercado': (30, 40),           # Mercados: 30-40
            'taller': (12, 27),            # Talleres: 15-27
            'charla': (8, 18),             # Charlas: 8-18
            'gira': (8, 20),               # Giras: 8-20
            'reunion': (10, 25),           # Reuniones: 10-25
        }
        
        min_asist, max_asist = ranges.get(tipo_evento, (4, 15))
        
        # No más de lo que hay registrado
        max_asist = min(max_asist, num_registrados)
        min_asist = min(min_asist, max(2, num_registrados // 2))
        
        return min_asist, max_asist

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 80))
        self.stdout.write(self.style.SUCCESS('GENERANDO ASISTENCIAS REALISTAS V2'))
        self.stdout.write(self.style.SUCCESS('=' * 80 + '\n'))

        # 1. LIMPIAR TODOS LOS DATOS ANTIGUOS
        self.stdout.write('🗑️  Eliminando asistencias anteriores...')
        old_count = Asistencia.objects.count()
        Asistencia.objects.all().delete()
        self.stdout.write(f'  ✓ Eliminadas {old_count} asistencias antiguas\n')

        # 2. ANÁLISIS DE DATOS
        self.stdout.write('📊 Analizando estructura...')

        asuntos_data = Asunto.objects.annotate(
            num_clientes=Count('asistentes', distinct=True)
        ).filter(num_clientes__gt=0)

        self.stdout.write(f'  ✓ {asuntos_data.count()} asuntos con clientes')

        clientes_activos = Clientes.objects.annotate(
            num_asuntos=Count('asuntos_asociados', distinct=True)
        ).filter(num_asuntos__gt=0).order_by('-num_asuntos')

        self.stdout.write(f'  ✓ {clientes_activos.count()} clientes registrados')

        # Top clientes más activos
        top_clientes = list(clientes_activos[:80])
        self.stdout.write(f'  ✓ Top 80 clientes para priorizar\n')

        # 3. GENERAR ASISTENCIAS
        self.stdout.write('💾 Generando asistencias realistas...')

        nuevas_asistencias = []
        eventos_con_asist = 0
        total_asistencias = 0

        for asunto in asuntos_data:
            tipo = self.obtener_tipo_evento(asunto.nombre)
            clientes_registrados = list(asunto.asistentes.all())
            
            if not clientes_registrados:
                continue

            # Para cada instancia del asunto
            for registro in asunto.registros.all():
                # Definir cantidad de asistentes
                min_asist, max_asist = self.obtener_rango_asistentes(
                    tipo, len(clientes_registrados)
                )
                cantidad = random.randint(min_asist, max_asist)
                cantidad = min(cantidad, len(clientes_registrados))

                # Seleccionar clientes: priorizar top activos
                clientes_top = [c for c in top_clientes if c in clientes_registrados]
                clientes_otros = [c for c in clientes_registrados if c not in top_clientes]

                # 75% top activos, 25% otros
                cant_top = int(cantidad * 0.75)
                cant_otros = cantidad - cant_top

                seleccionados = []
                
                if clientes_top:
                    seleccionados.extend(
                        random.sample(clientes_top, min(cant_top, len(clientes_top)))
                    )
                
                if clientes_otros and len(seleccionados) < cantidad:
                    falta = cantidad - len(seleccionados)
                    seleccionados.extend(
                        random.sample(clientes_otros, min(falta, len(clientes_otros)))
                    )

                # Crear asistencias (85% presentes, 15% ausentes)
                for cliente in seleccionados:
                    presente = random.random() < 0.85
                    asistencia = Asistencia(
                        cliente=cliente,
                        registro_asunto=registro,
                        presente=presente
                    )
                    nuevas_asistencias.append(asistencia)
                    total_asistencias += 1

                eventos_con_asist += 1

        # 4. GUARDAR EN LOTE
        Asistencia.objects.bulk_create(nuevas_asistencias, batch_size=1000)
        self.stdout.write(f'  ✓ Total generadas: {total_asistencias} asistencias')
        self.stdout.write(f'  ✓ Eventos con asistencia: {eventos_con_asist}\n')

        # 5. ESTADÍSTICAS FINALES
        self.stdout.write('=' * 80)
        self.stdout.write('📊 ESTADÍSTICAS FINALES:')
        self.stdout.write('=' * 80)

        total = Asistencia.objects.count()
        presentes = Asistencia.objects.filter(presente=True).count()
        ausentes = total - presentes
        tasa = (presentes / total * 100) if total > 0 else 0

        self.stdout.write(f'\n  Total asistencias: {total}')
        self.stdout.write(f'  Presentes: {presentes} ({tasa:.1f}%)')
        self.stdout.write(f'  Ausentes: {ausentes} ({100-tasa:.1f}%)')

        # Promedio por evento
        registros_con_asist = RegistroAsunto.objects.annotate(
            total=Count('asistencias')
        ).filter(total__gt=0)
        
        if registros_con_asist.exists():
            promedio = total / registros_con_asist.count()
            self.stdout.write(f'  Promedio por evento: {promedio:.1f}')

        # Top 10 eventos
        self.stdout.write(f'\n🏆 Top 10 eventos por asistencia:')
        top_eventos = RegistroAsunto.objects.annotate(
            total=Count('asistencias')
        ).order_by('-total')[:10]
        
        for evento in top_eventos:
            self.stdout.write(f'    {evento.asunto.nombre[:45]:45} | {evento.total:3d} asistentes')

        self.stdout.write(self.style.SUCCESS('\n✅ Generación completada.\n'))
