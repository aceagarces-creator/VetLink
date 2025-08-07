"""
Modelo relacionado con las nacionalidades del sistema.

Este módulo contiene el modelo para gestionar la información de las nacionalidades
registradas, utilizadas para tutores, personal y otras entidades del sistema.
"""

from django.db import models


class Nacionalidad(models.Model):
    """
    Modelo que representa una nacionalidad.
    
    Permite almacenar las distintas nacionalidades que pueden tener los tutores,
    personal clínico u otras entidades del sistema.
    
    Atributos:
        id_nacionalidad: Identificador único de la nacionalidad (clave primaria)
        nacionalidad: Nombre de la nacionalidad
        fecha_registro: Fecha de registro en el sistema (opcional)
        fecha_ultima_actualizacion: Fecha de última actualización (opcional)
    """
    
    # Clave primaria
    id_nacionalidad = models.AutoField(primary_key=True)
    
    # Nombre de la nacionalidad
    nacionalidad = models.CharField(max_length=100)
    
    # Metadatos
    fecha_registro = models.DateTimeField(blank=True, null=True)
    fecha_ultima_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Configuración del modelo."""
        managed = False
        db_table = 'nacionalidad'
    
    def __str__(self):
        """Representación en string de la nacionalidad."""
        return self.nacionalidad