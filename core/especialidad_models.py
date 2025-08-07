"""
Modelo relacionado con las especialidades del personal clínico veterinario.

Este módulo contiene el modelo para gestionar las especialidades que pueden tener
los miembros del personal de las clínicas veterinarias.
"""

from django.db import models

class Especialidad(models.Model):
    """
    Modelo que representa una especialidad clínica veterinaria.
    
    Las especialidades permiten clasificar al personal según su área de experiencia
    o formación, como por ejemplo: cirugía, anestesiología, medicina interna, etc.
    
    Atributos:
        id_especialidad: Identificador único de la especialidad (clave primaria)
        nombre: Nombre de la especialidad
        descripcion: Descripción detallada de la especialidad (opcional)
        activo: Indica si la especialidad está activa en el sistema (opcional)
        fecha_registro: Fecha de registro en el sistema (opcional)
        fecha_ultima_actualizacion: Fecha de última actualización (opcional)
    """
    id_especialidad = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)
    fecha_ultima_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Configuración del modelo."""
        managed = False
        db_table = 'especialidad'
    
    def __str__(self):
        """Representación en string de la especialidad."""
        return self.nombre