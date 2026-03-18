import random
from django.core.management.base import BaseCommand
from app.models import Asistencia


class Command(BaseCommand):
    help = 'Actualizar casi todas las asistencias a presentes (90% presente, 10% ausente)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== Actualizando Estado de Asistencias ===\n'))
        
        # Obtener todas las asistencias
        asistencias = Asistencia.objects.all()
        total = asistencias.count()
        
        if total == 0:
            self.stdout.write(self.style.WARNING('No hay asistencias para actualizar'))
            return
        
        self.stdout.write(f'Total de asistencias: {total}')
        
        # Marcar 90% como presentes, 10% como ausentes
        presentes_count = 0
        ausentes_count = 0
        
        # Obtener IDs aleatorios para ausentes (10%)
        ids_ausentes = set(random.sample(
            list(range(total)), 
            k=max(1, total // 10)  # 10% pero mínimo 1
        ))
        
        for idx, asistencia in enumerate(asistencias):
            if idx in ids_ausentes:
                asistencia.presente = False
                ausentes_count += 1
            else:
                asistencia.presente = True
                presentes_count += 1
        
        # Guardar en lote
        Asistencia.objects.bulk_update(asistencias, ['presente'], batch_size=500)
        
        self.stdout.write(f'\n✓ Presentes actualizados: {presentes_count} (90%)')
        self.stdout.write(f'✓ Ausentes actualizados: {ausentes_count} (10%)')
        self.stdout.write(f'✓ Total actualizado: {total}')
        
        # Estadísticas finales
        presentes_final = Asistencia.objects.filter(presente=True).count()
        ausentes_final = Asistencia.objects.filter(presente=False).count()
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Actualización completada.\n'))
        self.stdout.write(f'Estado final:')
        self.stdout.write(f'  ✓ Presentes: {presentes_final}')
        self.stdout.write(f'  ✗ Ausentes: {ausentes_final}')
        self.stdout.write(f'  Tasa de asistencia: {(presentes_final/total*100):.1f}%\n')
