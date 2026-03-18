from django.contrib import admin
from .models import Clientes

# Register your models here.

@admin.register(Clientes)
class ClientesAdmin(admin.ModelAdmin):
    list_display = ('rut', 'nombres', 'apellidos', 'sector', 'es_beneficiario', 'fecha_postulacion')
    list_filter = ('es_beneficiario', 'sector', 'fecha_postulacion')
    search_fields = ('rut', 'nombres', 'apellidos')
    readonly_fields = ('fecha_postulacion',)
    fieldsets = (
        ('Información Personal', {
            'fields': ('rut', 'nombres', 'apellidos')
        }),
        ('Información del Programa', {
            'fields': ('sector', 'extens', 'es_beneficiario', 'fecha_postulacion')
        }),
    )