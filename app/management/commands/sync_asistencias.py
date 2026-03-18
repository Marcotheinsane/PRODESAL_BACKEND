from django.core.management.base import BaseCommand
from app.models import Asistencia, Asunto, Clientes
from django.db.models import Count


class Command(BaseCommand):
    help = 'Sincroniza los registros de asistencia con la relación ManyToMany de Asunto.asistentes'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 80))
        self.stdout.write(self.style.SUCCESS('SINCRONIZANDO ASISTENCIAS CON ASUNTO.ASISTENTES'))
        self.stdout.write(self.style.SUCCESS('=' * 80 + '\n'))

        # Obtener todos los asuntos
        asuntos = Asunto.objects.all()
        
        total_asuntos = 0
        total_clientes_agregados = 0
        
        for asunto in asuntos:
            # Obtener clientes únicos que tienen asistencias en registro de este asunto
            clientes_con_asistencia = Clientes.objects.filter(
                asistencias__registro_asunto__asunto=asunto
            ).distinct()
            
            # Obtener clientes ya en la relación ManyToMany
            clientes_actuales = set(asunto.asistentes.values_list('id', flat=True))
            clientes_nuevos = set(clientes_con_asistencia.values_list('id', flat=True))
            
            # Clientes que hay que agregar
            clientes_a_agregar = clientes_nuevos - clientes_actuales
            
            if clientes_a_agregar:
                asunto.asistentes.add(*clientes_a_agregar)
                total_asuntos += 1
                total_clientes_agregados += len(clientes_a_agregar)
                
                self.stdout.write(
                    f"✓ {asunto.nombre[:50]:50} | "
                    f"+{len(clientes_a_agregar):2d} clientes"
                )
        
        self.stdout.write(self.style.SUCCESS('\n' + '-' * 80))
        self.stdout.write(self.style.SUCCESS(
            f'SINCRONIZACIÓN COMPLETADA\n'
            f'  Asuntos actualizados: {total_asuntos}\n'
            f'  Clientes agregados: {total_clientes_agregados}\n'
        ))
        
        # Mostrar estado final
        clientes_con_asist = Clientes.objects.filter(asistencias__isnull=False).distinct().count()
        clientes_en_asuntos = Clientes.objects.filter(asuntos_asociados__isnull=False).distinct().count()
        clientes_sin_sync = clientes_con_asist - clientes_en_asuntos
        
        self.stdout.write(f'  Estado final:')
        self.stdout.write(f'    - Clientes con asistencias: {clientes_con_asist}')
        self.stdout.write(f'    - Clientes en ManyToMany: {clientes_en_asuntos}')
        self.stdout.write(f'    - Aún sin sincronizar: {clientes_sin_sync}')
        self.stdout.write(self.style.SUCCESS('-' * 80 + '\n'))
