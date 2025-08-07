"""
Modelos relacionados con el personal de las clínicas veterinarias.

Este módulo contiene los modelos para gestionar la información del personal
que trabaja en las clínicas veterinarias, incluyendo sus datos personales,
especialidades y nacionalidades. Los modelos están organizados jerárquicamente:
PersonalClinica -> PersonalEspecialidad/PersonalNacionalidad.
"""

from django.db import models


class PersonalClinica(models.Model):
    """
    Modelo que representa a un miembro del personal de una clínica veterinaria.
    
    Contiene toda la información relevante de un trabajador de una clínica,
    incluyendo datos personales, información laboral y de contacto.
    Un personal puede tener múltiples especialidades y nacionalidades.
    
    Atributos:
        id_personal: Identificador único del personal (clave primaria)
        id_clinica: Referencia a la clínica donde trabaja
        nro_documento: Número de documento de identidad
        tipo_documento: Tipo de documento (opcional)
        fecha_inicio: Fecha de inicio en la clínica (opcional)
        fecha_termino: Fecha de término en la clínica (opcional)
        cargo: Cargo o puesto en la clínica (opcional)
        nombres: Nombres del personal (opcional)
        apellido_paterno: Apellido paterno (opcional)
        apellido_materno: Apellido materno (opcional)
        genero: Género del personal (opcional)
        fecha_nacimiento: Fecha de nacimiento (opcional)
        email: Correo electrónico (opcional)
        celular: Teléfono móvil (opcional)
        telefono: Teléfono fijo (opcional)
        profesion: Profesión del personal (opcional)
        fecha_registro: Fecha de registro en el sistema (opcional)
        fecha_ultima_actualizacion: Fecha de última actualización (opcional)
    """
    
    # Clave primaria
    id_personal = models.AutoField(primary_key=True)
    
    # Relación con clínica
    id_clinica = models.ForeignKey('ClinicaVeterinaria', models.DO_NOTHING, db_column='id_clinica')
    
    # Datos de identificación
    nro_documento = models.CharField(max_length=20)
    tipo_documento = models.CharField(max_length=20, blank=True, null=True)
    
    # Información laboral
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_termino = models.DateField(blank=True, null=True)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    profesion = models.CharField(max_length=100, blank=True, null=True)
    
    # Datos personales
    nombres = models.CharField(max_length=100, blank=True, null=True)
    apellido_paterno = models.CharField(max_length=100, blank=True, null=True)
    apellido_materno = models.CharField(max_length=100, blank=True, null=True)
    genero = models.CharField(max_length=20, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    
    # Información de contacto
    email = models.CharField(max_length=100, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    
    # Metadatos
    fecha_registro = models.DateTimeField(blank=True, null=True)
    fecha_ultima_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Configuración del modelo."""
        managed = False
        db_table = 'personal_clinica'
        unique_together = (('nro_documento', 'id_clinica'),)
    
    def __str__(self):
        """Representación en string del personal de clínica."""
        if self.nombres and self.apellido_paterno:
            return f"{self.nombres} {self.apellido_paterno}"
        elif self.nombres:
            return self.nombres
        else:
            return f"Personal {self.id_personal}"


class PersonalEspecialidad(models.Model):
    """
    Modelo de tabla intermedia entre PersonalClinica y Especialidad.
    
    Permite establecer una relación muchos a muchos entre personal de clínica
    y especialidades, donde un personal puede tener múltiples especialidades
    y una especialidad puede ser compartida por múltiples personal.
    
    Utiliza una clave primaria compuesta formada por id_personal e id_especialidad.
    
    Atributos:
        pk: Clave primaria compuesta (id_personal, id_especialidad)
        id_personal: Referencia al personal de clínica
        id_especialidad: Referencia a la especialidad
        fecha_asignacion: Fecha de asignación de la especialidad (opcional)
    """
    
    # Clave primaria compuesta
    pk = models.CompositePrimaryKey('id_personal', 'id_especialidad')
    
    # Relaciones
    id_personal = models.ForeignKey(PersonalClinica, models.DO_NOTHING, db_column='id_personal')
    id_especialidad = models.ForeignKey('Especialidad', models.DO_NOTHING, db_column='id_especialidad')
    
    # Información de asignación
    fecha_asignacion = models.DateField(blank=True, null=True)

    class Meta:
        """Configuración del modelo."""
        managed = False
        db_table = 'personal_especialidad'
    
    def __str__(self):
        """Representación en string de la asociación personal-especialidad."""
        return f"{self.id_personal} - {self.id_especialidad}"


class PersonalNacionalidad(models.Model):
    """
    Modelo de tabla intermedia entre PersonalClinica y Nacionalidad.
    
    Permite establecer una relación muchos a muchos entre personal de clínica
    y nacionalidades, donde un personal puede tener múltiples nacionalidades
    y una nacionalidad puede ser compartida por múltiples personal.
    
    Utiliza una clave primaria compuesta formada por id_personal e id_nacionalidad.
    
    Atributos:
        pk: Clave primaria compuesta (id_personal, id_nacionalidad)
        id_personal: Referencia al personal de clínica
        id_nacionalidad: Referencia a la nacionalidad
        fecha_registro: Fecha de registro de la nacionalidad (opcional)
    """
    
    # Clave primaria compuesta
    pk = models.CompositePrimaryKey('id_personal', 'id_nacionalidad')
    
    # Relaciones
    id_personal = models.ForeignKey(PersonalClinica, models.DO_NOTHING, db_column='id_personal')
    id_nacionalidad = models.ForeignKey('Nacionalidad', models.DO_NOTHING, db_column='id_nacionalidad')
    
    # Metadatos
    fecha_registro = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Configuración del modelo."""
        managed = False
        db_table = 'personal_nacionalidad'
    
    def __str__(self):
        """Representación en string de la asociación personal-nacionalidad."""
        return f"{self.id_personal} - {self.id_nacionalidad}" 