from django.db import models
from django.core.exceptions import ValidationError
import re


class Clientes(models.Model):
    """Modelo de personas/productores con información de ficha social"""
    ESTADO_CIVIL_CHOICES = [
        ('soltero', 'Soltero/a'),
        ('casado', 'Casado/a'),
        ('soltera', 'Soltera'),
        ('divorciado', 'Divorciado/a'),
        ('separado', 'Separado/a'),
        ('viudo', 'Viudo/a'),
        ('union_libre', 'Unión Libre'),
    ]
    
    ESCOLARIDAD_CHOICES = [
        ('sin_estudios', 'Sin Estudios'),
        ('basica_incompleta', 'Básica Incompleta'),
        ('basica_completa', 'Básica Completa'),
        ('media_incompleta', 'Media Incompleta'),
        ('media_completa', 'Media Completa'),
        ('tecnica', 'Técnica'),
        ('superior', 'Superior'),
    ]
    
    TIPO_TENENCIA_CHOICES = [
        ('propietario', 'Propietario'),
        ('arrendatario', 'Arrendatario'),
        ('prestado', 'Prestado'),
        ('ocupante', 'Ocupante'),
    ]

    # Información Personal
    rut = models.CharField(max_length=20, unique=True)
    apellidos = models.CharField(max_length=100)
    nombres = models.CharField(max_length=100)
    edad = models.IntegerField(blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    numero_documento = models.CharField(max_length=50, blank=True, null=True)
    
    # Información de Contacto
    telefono = models.CharField(max_length=20, blank=True, null=True)
    sector = models.CharField(max_length=100, blank=True, null=True)
    
    # Información Social
    estado_civil = models.CharField(max_length=50, choices=ESTADO_CIVIL_CHOICES, blank=True, null=True)
    escolaridad = models.CharField(max_length=50, choices=ESCOLARIDAD_CHOICES, blank=True, null=True)
    ocupacion = models.CharField(max_length=100, blank=True, null=True)
    
    # Información de Vivienda
    tipo_tenencia = models.CharField(max_length=50, choices=TIPO_TENENCIA_CHOICES, blank=True, null=True)
    vivienda_saneada = models.BooleanField(null=True, blank=True)
    ingresos = models.CharField(max_length=100, blank=True, null=True)  # PGU, PREDIALES, HIJOS, etc.
    
    # Información adicional
    fecha_postulacion = models.DateField(auto_now_add=True)
    es_beneficiario = models.BooleanField(default=False)
    extens = models.CharField(max_length=100, blank=True, null=True)  # Extensionista responsable
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_postulacion']
        indexes = [
            models.Index(fields=['rut']),
            models.Index(fields=['sector']),
            models.Index(fields=['es_beneficiario']),
        ]

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.rut})"
    
    def clean(self):
        """Validar RUT antes de guardar"""
        self.validar_rut_formato(self.rut)
    
    def save(self, *args, **kwargs):
        """Guardar y validar RUT"""
        self.clean()
        super().save(*args, **kwargs)

    @staticmethod
    def validar_rut_formato(rut: str) -> bool:
        """Validar que el RUT esté bien formado. Formato: XX.XXX.XXX-X"""
        rut_pattern = re.compile(r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$')
        if not rut_pattern.match(rut.strip()):
            raise ValidationError("RUT no está bien formado. Debe tener el formato XX.XXX.XXX-X")
        return True
    
    @staticmethod
    def existe_rut(rut: str) -> bool:
        """Verificar si un RUT ya existe en la base de datos"""
        return Clientes.objects.filter(rut=rut).exists()


class Hogar(models.Model):
    """Modelo del hogar/grupo familiar"""
    persona_principal = models.OneToOneField(
        Clientes, 
        on_delete=models.CASCADE, 
        related_name='hogar',
        help_text="Persona responsable del hogar"
    )
    fecha_registro = models.DateField(auto_now_add=True)
    luz = models.BooleanField(null=True, blank=True, help_text="¿Tiene acceso a luz eléctrica?")
    agua = models.BooleanField(null=True, blank=True, help_text="¿Tiene acceso a agua potable?")
    rol = models.CharField(max_length=100, blank=True, null=True, help_text="Rol en el registro")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-fecha_registro']
    
    def __str__(self):
        return f"Hogar de {self.persona_principal.nombres} {self.persona_principal.apellidos}"


class CargaFamiliar(models.Model):
    """Modelo para registrar hijos, padres ancianos y otros dependientes"""
    PARENTESCO_CHOICES = [
        ('hijo', 'Hijo/a'),
        ('padre', 'Padre'),
        ('madre', 'Madre'),
        ('abuelo', 'Abuelo/a'),
        ('hermano', 'Hermano/a'),
        ('otros', 'Otros'),
    ]
    
    hogar = models.ForeignKey(
        Hogar, 
        on_delete=models.CASCADE, 
        related_name='carga_familiar'
    )
    parentesco = models.CharField(max_length=50, choices=PARENTESCO_CHOICES)
    nombre = models.CharField(max_length=100)
    edad = models.IntegerField(blank=True, null=True)
    rut = models.CharField(max_length=12, blank=True, null=True)
    ocupacion = models.CharField(max_length=100, blank=True, null=True)
    escolaridad = models.CharField(max_length=50, choices=Clientes.ESCOLARIDAD_CHOICES, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['hogar', 'parentesco']
    
    def __str__(self):
        return f"{self.nombre} ({self.parentesco}) - {self.hogar.persona_principal.nombres}"


class InformacionSalud(models.Model):
    """Modelo para registrar información de salud de personas en el hogar"""
    persona = models.OneToOneField(
        Clientes,
        on_delete=models.CASCADE,
        related_name='informacion_salud'
    )
    enfermedad = models.TextField(blank=True, null=True, help_text="Enfermedades diagnosticadas")
    toma_medicamentos = models.BooleanField(null=True, blank=True)
    medicamentos = models.TextField(blank=True, null=True, help_text="Lista de medicamentos")
    controles_medicos = models.TextField(blank=True, null=True, help_text="Tipo de controles (ronda médica, sabat, etc)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Salud de {self.persona.nombres}"


class RedConocida(models.Model):
    """Modelo para registrar redes de apoyo conocidas y participación"""
    persona = models.OneToOneField(
        Clientes,
        on_delete=models.CASCADE,
        related_name='redes_conocidas'
    )
    redes_conoce = models.TextField(blank=True, null=True, help_text="Redes que conoce (JJVV, Clubes, etc)")
    redes_participa = models.TextField(blank=True, null=True, help_text="Redes en que participa")
    redes_apoyo = models.TextField(blank=True, null=True, help_text="Redes de apoyo disponibles")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Redes de {self.persona.nombres}"


class RegistroSocial(models.Model):
    """Modelo para información del Registro Social de Hogares"""
    persona = models.OneToOneField(
        Clientes,
        on_delete=models.CASCADE,
        related_name='registro_social'
    )
    posee_registro = models.BooleanField(null=True, blank=True, help_text="¿Posee Registro Social de Hogares?")
    puntaje = models.CharField(max_length=50, blank=True, null=True, help_text="Puntaje del registro")
    actualizado = models.BooleanField(null=True, blank=True, help_text="¿Está actualizado?")
    fecha_actualizacion = models.DateField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Registro Social de {self.persona.nombres}"


class AnotacionesHogar(models.Model):
    """Modelo para registrar necesidades, observaciones y recomendaciones"""
    hogar = models.OneToOneField(
        Hogar,
        on_delete=models.CASCADE,
        related_name='anotaciones'
    )
    necesidades = models.TextField(blank=True, null=True, help_text="Necesidades identificadas")
    observaciones = models.TextField(blank=True, null=True, help_text="Observaciones generales")
    recomendaciones = models.TextField(blank=True, null=True, help_text="Recomendaciones propuestas")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Anotaciones de {self.hogar.persona_principal.nombres}"


class Asunto(models.Model):
    """Modelo para registrar asuntos/eventos/reuniones"""
    TIPO_CHOICES = [
        ('reunion', 'Reunión'),
        ('taller', 'Taller'),
        ('entrega_semillas', 'Entrega de Semillas'),
        ('mercado', 'Mercado Campesino'),
        ('gira', 'Gira/Visita Técnica'),
        ('charla', 'Charla/Capacitación'),
        ('otro', 'Otro'),
    ]
    
    nombre = models.CharField(max_length=255, db_index=True)  # ej: "Mi PyME Rural", "Taller de Riego"
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES, default='reunion')
    descripcion = models.TextField(blank=True, null=True)
    total_instancias = models.IntegerField(default=1)  # Contador de repeticiones
    asistentes = models.ManyToManyField(Clientes, related_name='asuntos_asociados', blank=True)  # Clientes asociados al asunto
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        unique_together = ['nombre']  # Evitar duplicados exactos

    def __str__(self):
        return f"{self.nombre} ({self.total_instancias} instancias)"


class RegistroAsunto(models.Model):
    """Instancia específica de un asunto (fecha, lugar, responsable)"""
    asunto = models.ForeignKey(Asunto, on_delete=models.CASCADE, related_name='registros')
    fecha = models.DateField(blank=True, null=True)
    lugar = models.CharField(max_length=255, blank=True, null=True)
    responsable = models.CharField(max_length=255, blank=True, null=True)
    cantidad_asistentes_registrados = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['asunto', 'fecha']),
        ]

    def __str__(self):
        return f"{self.asunto.nombre} - {self.fecha}"


class Asistencia(models.Model):
    """Vinculación cliente-asunto con estado de asistencia"""
    cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE, related_name='asistencias')
    registro_asunto = models.ForeignKey(RegistroAsunto, on_delete=models.CASCADE, related_name='asistencias')
    presente = models.BooleanField(default=False)  # True = asistió, False = no asistió
    fecha_registro = models.DateTimeField(auto_now_add=True)
    notas = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-fecha_registro']
        unique_together = ['cliente', 'registro_asunto']  # Un cliente solo puede tener una asistencia por evento

    def __str__(self):
        estado = "Asistió" if self.presente else "No asistió"
        return f"{self.cliente.nombres} - {self.registro_asunto.asunto.nombre} ({estado})"
