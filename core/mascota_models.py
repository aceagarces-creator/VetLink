"""
Modelos relacionados con las mascotas del sistema.

Este módulo contiene los modelos para gestionar la información de las mascotas,
incluyendo sus datos básicos, características físicas, información médica
y relaciones con tutores y clínicas veterinarias.
"""

from django.db import models


class Mascota(models.Model):
    """
    Modelo que representa una mascota en el sistema.
    
    Contiene toda la información relacionada con una mascota, incluyendo
    datos de identificación, características físicas, información médica
    y relaciones con su tutor y clínica veterinaria.
    
    Atributos:
        id_mascota: Identificador único de la mascota (clave primaria)
        id_tutor: Referencia al tutor responsable de la mascota
        id_especie: Referencia a la especie de la mascota
        id_raza: Referencia a la raza de la mascota
        id_clinica_consentimiento: Referencia a la clínica donde se dio el consentimiento
        nro_chip: Número de chip de identificación (único)
        nombre: Nombre de la mascota
        fecha_nacimiento: Fecha de nacimiento de la mascota
        sexo: Sexo de la mascota (macho/hembra)
        color: Color de la mascota
        estado_reproductivo: Estado reproductivo (esterilizado, etc.)
        estado_vital: Estado vital (vivo, fallecido, etc.)
        foto: URL o datos de la foto de la mascota
        consentimiento: Indica si se ha dado consentimiento para tratamiento
        fecha_consentimiento: Fecha en que se dio el consentimiento
        url_doc_consentimiento: URL del documento de consentimiento
        notas_adicionales: Notas adicionales sobre la mascota
        fecha_registro: Fecha de registro en el sistema
        fecha_ultima_actualizacion: Fecha de última actualización
    """
    
    # Clave primaria
    id_mascota = models.AutoField(primary_key=True)
    
    # Relaciones principales
    id_tutor = models.ForeignKey('Tutor', models.DO_NOTHING, db_column='id_tutor')
    id_especie = models.ForeignKey('Especie', models.DO_NOTHING, db_column='id_especie')
    id_raza = models.ForeignKey('Raza', models.DO_NOTHING, db_column='id_raza')
    id_clinica_consentimiento = models.ForeignKey('ClinicaVeterinaria', models.DO_NOTHING, 
                                                 db_column='id_clinica_consentimiento', 
                                                 blank=True, null=True)
    
    # Datos de identificación
    nro_chip = models.CharField(unique=True, max_length=30)
    nombre = models.CharField(max_length=100)
    
    # Datos básicos
    fecha_nacimiento = models.DateField(blank=True, null=True)
    sexo = models.CharField(max_length=10, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    
    # Estado de la mascota
    estado_reproductivo = models.CharField(max_length=50, blank=True, null=True)
    estado_vital = models.CharField(max_length=50, blank=True, null=True)
    
    # Multimedia
    foto = models.TextField(blank=True, null=True)
    
    # Información de consentimiento
    consentimiento = models.BooleanField(blank=True, null=True)
    fecha_consentimiento = models.DateField(blank=True, null=True)
    url_doc_consentimiento = models.TextField(blank=True, null=True)
    
    # Información adicional
    notas_adicionales = models.TextField(blank=True, null=True)
    
    # Metadatos
    fecha_registro = models.DateTimeField(blank=True, null=True)
    fecha_ultima_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Configuración del modelo."""
        managed = False
        db_table = 'mascota'
    
    def __str__(self):
        """Representación en string de la mascota."""
        return f"{self.nombre} ({self.nro_chip})" 