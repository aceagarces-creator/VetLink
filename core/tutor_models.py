"""
Modelos relacionados con los tutores de mascotas.

Este módulo contiene los modelos para gestionar la información de los tutores
de mascotas, incluyendo sus datos personales, dirección, contacto y nacionalidades.
"""

from django.db import models


class Tutor(models.Model):
    """
    Modelo que representa a un tutor de mascota.
    
    Contiene toda la información personal y de contacto del tutor,
    incluyendo dirección, datos de identificación y información de contacto.
    Un tutor puede tener múltiples mascotas asociadas.
    
    Atributos:
        id_tutor: Identificador único del tutor (clave primaria)
        id_comuna: Referencia a la comuna de residencia
        nro_documento: Número de documento de identidad (único)
        tipo_documento: Tipo de documento (RUT, pasaporte, etc.)
        nombres: Nombres del tutor
        apellido_paterno: Apellido paterno
        apellido_materno: Apellido materno (opcional)
        fecha_nacimiento: Fecha de nacimiento
        email: Dirección de correo electrónico
        telefono: Número de teléfono fijo
        celular: Número de teléfono móvil
        calle: Nombre de la calle
        numero: Número de la dirección
        departamento: Número o letra del departamento
        codigo_postal: Código postal
        complemento: Información adicional de la dirección
        foto: URL o datos de la foto del tutor
        fecha_registro: Fecha de registro en el sistema
        fecha_ultima_actualizacion: Fecha de última actualización
    """
    
    # Clave primaria
    id_tutor = models.AutoField(primary_key=True)
    
    # Relación con comuna
    id_comuna = models.ForeignKey('Comuna', models.DO_NOTHING, db_column='id_comuna')
    
    # Datos de identificación
    nro_documento = models.CharField(unique=True, max_length=20)
    tipo_documento = models.CharField(max_length=20, blank=True, null=True)
    
    # Datos personales
    nombres = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    
    # Información de contacto
    email = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    
    # Dirección
    calle = models.CharField(max_length=100, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    departamento = models.CharField(max_length=10, blank=True, null=True)
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    
    # Multimedia y metadatos
    foto = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)
    fecha_ultima_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Configuración del modelo."""
        managed = False
        db_table = 'tutor'
    
    def __str__(self):
        """Representación en string del tutor."""
        return f"{self.nombres} {self.apellido_paterno}"


class TutorNacionalidad(models.Model):
    """
    Modelo de tabla intermedia entre Tutor y Nacionalidad.
    
    Permite establecer una relación muchos a muchos entre tutores y nacionalidades,
    donde un tutor puede tener múltiples nacionalidades y una nacionalidad
    puede estar asociada a múltiples tutores.
    
    Utiliza una clave primaria compuesta formada por id_tutor e id_nacionalidad.
    
    Atributos:
        pk: Clave primaria compuesta (id_tutor, id_nacionalidad)
        id_tutor: Referencia al tutor
        id_nacionalidad: Referencia a la nacionalidad
        fecha_registro: Fecha de registro de la asociación
    """
    
    # Clave primaria compuesta
    pk = models.CompositePrimaryKey('id_tutor', 'id_nacionalidad')
    
    # Relaciones
    id_tutor = models.ForeignKey(Tutor, models.DO_NOTHING, db_column='id_tutor')
    id_nacionalidad = models.ForeignKey('Nacionalidad', models.DO_NOTHING, db_column='id_nacionalidad')
    
    # Metadatos
    fecha_registro = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Configuración del modelo."""
        managed = False
        db_table = 'tutor_nacionalidad'
    
    def __str__(self):
        """Representación en string de la asociación tutor-nacionalidad."""
        return f"{self.id_tutor} - {self.id_nacionalidad}"
