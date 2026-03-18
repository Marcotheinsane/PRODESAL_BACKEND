from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# Importar modelos
from app.models import (
    Hogar, CargaFamiliar, InformacionSalud, 
    RedConocida, RegistroSocial, AnotacionesHogar, Clientes
)

# Importar serializers
from app.serializers import (
    HogarSerializer, CargaFamiliarSerializer, InformacionSaludSerializer,
    RedConocidaSerializer, RegistroSocialSerializer, AnotacionesHogarSerializer
)


class HogarViewSet(viewsets.ModelViewSet):
    """
    CRUD para Información de Hogar/Vivienda
    
    Endpoints:
    - GET /api/v1/hogar/ - Listar todos
    - POST /api/v1/hogar/ - Crear hogar
    - GET /api/v1/hogar/{id}/ - Ver detalle
    - PATCH /api/v1/hogar/{id}/ - Actualizar (parcial)
    - PUT /api/v1/hogar/{id}/ - Actualizar (completo)
    - DELETE /api/v1/hogar/{id}/ - Eliminar
    - GET /api/v1/hogar/por-cliente/{cliente_id}/ - Obtener hogar de cliente
    """
    queryset = Hogar.objects.select_related('persona_principal').all()
    serializer_class = HogarSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='por-cliente/(?P<cliente_id>[^/.]+)')
    def por_cliente(self, request, cliente_id=None):
        """Obtener hogar de un cliente específico"""
        try:
            hogar = Hogar.objects.get(persona_principal_id=cliente_id)
            serializer = self.get_serializer(hogar)
            return Response(serializer.data)
        except Hogar.DoesNotExist:
            return Response(
                {'error': f'No existe hogar para cliente ID {cliente_id}'},
                status=status.HTTP_404_NOT_FOUND
            )


class CargaFamiliarViewSet(viewsets.ModelViewSet):
    """
    CRUD para Carga Familiar (hijos, padres, etc.)
    
    Endpoints:
    - GET /api/v1/carga-familiar/ - Listar todos
    - POST /api/v1/carga-familiar/ - Agregar miembro familiar
    - GET /api/v1/carga-familiar/{id}/ - Ver detalle
    - PATCH /api/v1/carga-familiar/{id}/ - Actualizar
    - DELETE /api/v1/carga-familiar/{id}/ - Eliminar
    - GET /api/v1/carga-familiar/por-hogar/{hogar_id}/ - Listar familia de hogar
    """
    queryset = CargaFamiliar.objects.select_related('hogar').all()
    serializer_class = CargaFamiliarSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='por-hogar/(?P<hogar_id>[^/.]+)')
    def por_hogar(self, request, hogar_id=None):
        """Listar todos los miembros familiares de un hogar"""
        try:
            familia = CargaFamiliar.objects.filter(hogar_id=hogar_id)
            if not familia.exists():
                return Response(
                    {'error': f'No hay carga familiar para hogar ID {hogar_id}'},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(familia, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class InformacionSaludViewSet(viewsets.ModelViewSet):
    """
    CRUD para Información de Salud
    
    Campos:
    - enfermedad: Enfermedades diagnosticadas
    - toma_medicamentos: bool
    - medicamentos: Medicamentos que toma
    - controles_medicos: Tipo de controles (ronda médica, sabat, etc)
    
    Endpoints:
    - GET /api/v1/informacion-salud/ - Listar todos
    - POST /api/v1/informacion-salud/ - Crear registro
    - GET /api/v1/informacion-salud/{id}/ - Ver detalle
    - PATCH /api/v1/informacion-salud/{id}/ - Actualizar
    - DELETE /api/v1/informacion-salud/{id}/ - Eliminar
    """
    queryset = InformacionSalud.objects.select_related('persona').all()
    serializer_class = InformacionSaludSerializer
    permission_classes = [IsAuthenticated]


class RedConocidaViewSet(viewsets.ModelViewSet):
    """
    CRUD para Redes de Apoyo
    
    Campos:
    - redes_conoce: Redes que conoce (JJVV, clubes, etc)
    - redes_participa: Redes en que participa
    - redes_apoyo: Redes de apoyo disponibles (familia, vecinos, etc)
    
    Endpoints:
    - GET /api/v1/redes/ - Listar todos
    - POST /api/v1/redes/ - Crear registro
    - GET /api/v1/redes/{id}/ - Ver detalle
    - PATCH /api/v1/redes/{id}/ - Actualizar
    - DELETE /api/v1/redes/{id}/ - Eliminar
    """
    queryset = RedConocida.objects.select_related('persona').all()
    serializer_class = RedConocidaSerializer
    permission_classes = [IsAuthenticated]


class RegistroSocialViewSet(viewsets.ModelViewSet):
    """
    CRUD para Registro Social de Hogares
    
    Campos:
    - posee_registro: bool
    - puntaje: Puntaje del registro
    - actualizado: bool
    - fecha_actualizacion: Fecha de última actualizacion
    
    Endpoints:
    - GET /api/v1/registro-social/ - Listar todos
    - POST /api/v1/registro-social/ - Crear registro
    - GET /api/v1/registro-social/{id}/ - Ver detalle
    - PATCH /api/v1/registro-social/{id}/ - Actualizar
    - DELETE /api/v1/registro-social/{id}/ - Eliminar
    """
    queryset = RegistroSocial.objects.select_related('persona').all()
    serializer_class = RegistroSocialSerializer
    permission_classes = [IsAuthenticated]


class AnotacionesHogarViewSet(viewsets.ModelViewSet):
    """
    CRUD para Anotaciones (Necesidades, Observaciones, Recomendaciones)
    
    Campos:
    - necesidades: Necesidades identificadas
    - observaciones: Observaciones generales
    - recomendaciones: Recomendaciones propuestas
    
    Endpoints:
    - GET /api/v1/anotaciones/ - Listar todos
    - POST /api/v1/anotaciones/ - Crear anotación
    - GET /api/v1/anotaciones/{id}/ - Ver detalle
    - PATCH /api/v1/anotaciones/{id}/ - Actualizar
    - DELETE /api/v1/anotaciones/{id}/ - Eliminar
    """
    queryset = AnotacionesHogar.objects.select_related('hogar').all()
    serializer_class = AnotacionesHogarSerializer
    permission_classes = [IsAuthenticated]
