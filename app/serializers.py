from .models import (
    Clientes, Asunto, RegistroAsunto, Asistencia, 
    Hogar, CargaFamiliar, InformacionSalud, RedConocida, RegistroSocial, AnotacionesHogar
)
from rest_framework import serializers
from django.core.exceptions import ValidationError


class CargaFamiliarSerializer(serializers.ModelSerializer):
    class Meta:
        model = CargaFamiliar
        fields = ['id', 'hogar', 'parentesco', 'nombre', 'edad', 'rut', 'ocupacion', 'escolaridad']
        read_only_fields = ['id']
        extra_kwargs = {
            'hogar': {'required': False},
            'parentesco': {'required': False},
            'nombre': {'required': False},
            'edad': {'required': False},
            'rut': {'required': False},
            'ocupacion': {'required': False},
            'escolaridad': {'required': False},
        }


class InformacionSaludSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformacionSalud
        fields = ['id', 'persona', 'enfermedad', 'toma_medicamentos', 'medicamentos', 'controles_medicos']
        read_only_fields = ['id']
        extra_kwargs = {
            'persona': {'required': False},
            'enfermedad': {'required': False},
            'toma_medicamentos': {'required': False},
            'medicamentos': {'required': False},
            'controles_medicos': {'required': False},
        }


class RedConocidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RedConocida
        fields = ['id', 'persona', 'redes_conoce', 'redes_participa', 'redes_apoyo']
        read_only_fields = ['id']
        extra_kwargs = {
            'persona': {'required': False},
            'redes_conoce': {'required': False},
            'redes_participa': {'required': False},
            'redes_apoyo': {'required': False},
        }


class RegistroSocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroSocial
        fields = ['id', 'persona', 'posee_registro', 'puntaje', 'actualizado', 'fecha_actualizacion']
        read_only_fields = ['id']
        extra_kwargs = {
            'persona': {'required': False},
            'posee_registro': {'required': False},
            'puntaje': {'required': False},
            'actualizado': {'required': False},
            'fecha_actualizacion': {'required': False},
        }


class AnotacionesHogarSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnotacionesHogar
        fields = ['id', 'hogar', 'necesidades', 'observaciones', 'recomendaciones']
        read_only_fields = ['id']
        extra_kwargs = {
            'hogar': {'required': False},
            'necesidades': {'required': False},
            'observaciones': {'required': False},
            'recomendaciones': {'required': False},
        }


class HogarSerializer(serializers.ModelSerializer):
    carga_familiar = CargaFamiliarSerializer(many=True, read_only=True)
    anotaciones = AnotacionesHogarSerializer(read_only=True)
    
    class Meta:
        model = Hogar
        fields = ['id', 'luz', 'agua', 'rol', 'fecha_registro', 'carga_familiar', 'anotaciones']
        read_only_fields = ['id', 'fecha_registro']


class ClientesDetailSerializer(serializers.ModelSerializer):
    """Serializer completo con toda la información de ficha social"""
    hogar = HogarSerializer(read_only=True)
    informacion_salud = InformacionSaludSerializer(read_only=True)
    redes_conocidas = RedConocidaSerializer(read_only=True)
    registro_social = RegistroSocialSerializer(read_only=True)
    
    class Meta:
        model = Clientes
        fields = [
            'id', 'rut', 'apellidos', 'nombres', 'edad', 'fecha_nacimiento',
            'numero_documento', 'telefono', 'sector', 'estado_civil', 'escolaridad',
            'ocupacion', 'tipo_tenencia', 'vivienda_saneada', 'ingresos',
            'es_beneficiario', 'extens', 'fecha_postulacion', 'updated_at',
            'hogar', 'informacion_salud', 'redes_conocidas', 'registro_social'
        ]
        read_only_fields = ['id', 'fecha_postulacion', 'updated_at']


class ClientesListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados"""
    class Meta:
        model = Clientes
        fields = ['id', 'rut', 'apellidos', 'nombres', 'sector', 'telefono', 'es_beneficiario', 'fecha_postulacion']
        read_only_fields = ['id', 'fecha_postulacion']


class AsistenciaSerializer(serializers.ModelSerializer):
    cliente_nombres = serializers.CharField(source='cliente.nombres', read_only=True)
    cliente_apellidos = serializers.CharField(source='cliente.apellidos', read_only=True)
    cliente_rut = serializers.CharField(source='cliente.rut', read_only=True)
    
    class Meta:
        model = Asistencia
        fields = ['id', 'cliente', 'cliente_rut', 'cliente_nombres', 'cliente_apellidos', 'registro_asunto', 'presente', 'fecha_registro', 'notas']
        read_only_fields = ['id', 'fecha_registro']


class RegistroAsuntoSerializer(serializers.ModelSerializer):
    asistencias = AsistenciaSerializer(many=True, read_only=True)
    asunto_nombre = serializers.CharField(source='asunto.nombre', read_only=True)
    total_asistentes = serializers.SerializerMethodField()
    presentes = serializers.SerializerMethodField()
    ausentes = serializers.SerializerMethodField()
    
    class Meta:
        model = RegistroAsunto
        fields = ['id', 'asunto', 'asunto_nombre', 'fecha', 'lugar', 'responsable', 'cantidad_asistentes_registrados', 
                  'total_asistentes', 'presentes', 'ausentes', 'asistencias', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_total_asistentes(self, obj):
        return obj.asistencias.count()
    
    def get_presentes(self, obj):
        return obj.asistencias.filter(presente=True).count()
    
    def get_ausentes(self, obj):
        return obj.asistencias.filter(presente=False).count()


class AsuntoSerializer(serializers.ModelSerializer):
    registros = RegistroAsuntoSerializer(many=True, read_only=True)
    ultima_fecha = serializers.SerializerMethodField()
    asistentes = serializers.PrimaryKeyRelatedField(
        queryset=Clientes.objects.all(),
        many=True,
        required=False
    )
    
    class Meta:
        model = Asunto
        fields = ['id', 'nombre', 'tipo', 'descripcion', 'total_instancias', 'ultima_fecha', 'asistentes', 'registros', 'created_at']
        read_only_fields = ['id', 'total_instancias', 'created_at']
    
    def get_ultima_fecha(self, obj):
        ultimo_registro = obj.registros.first()
        return ultimo_registro.fecha if ultimo_registro else None