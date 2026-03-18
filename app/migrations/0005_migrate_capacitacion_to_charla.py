from django.db import migrations

def migrate_capacitacion_to_charla(apps, schema_editor):
    """Migrar todos los tipos 'capacitacion' a 'charla'"""
    Asunto = apps.get_model('app', 'Asunto')
    Asunto.objects.filter(tipo='capacitacion').update(tipo='charla')

def reverse_charla_to_capacitacion(apps, schema_editor):
    """Revertir cambios (opcional)"""
    Asunto = apps.get_model('app', 'Asunto')
    Asunto.objects.filter(tipo='charla').update(tipo='capacitacion')

class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_asunto_asistentes'),
    ]

    operations = [
        migrations.RunPython(migrate_capacitacion_to_charla, reverse_charla_to_capacitacion),
    ]
