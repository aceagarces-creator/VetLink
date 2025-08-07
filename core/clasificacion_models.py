"""
Modelos relacionados con la clasificación taxonómica de mascotas.

Este módulo contiene los modelos para gestionar la información taxonómica
de las mascotas, incluyendo especies y razas. Los modelos están organizados
jerárquicamente: Especie -> Raza.
"""

from django.db import models


class Especie(models.Model):
    """
    Modelo que representa una especie animal.
    
    Las especies son la clasificación taxonómica de mayor nivel para las mascotas.
    Cada especie puede contener múltiples razas. Ejemplos: Canis familiaris (Perro),
    Felis catus (Gato), etc.
    
    Atributos:
        id_especie: Identificador único de la especie (clave primaria)
        nombre: Nombre de la especie
        activo: Indica si la especie está activa en el sistema
        fecha_registro: Fecha de registro en el sistema
        fecha_ultima_actualizacion: Fecha de última actualización
    """
    
    # Clave primaria
    id_especie = models.AutoField(primary_key=True)
    
    # Datos de la especie
    nombre = models.CharField(max_length=100)
    
    # Estado y metadatos
    activo = models.BooleanField(blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)
    fecha_ultima_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Configuración del modelo."""
        managed = False
        db_table = 'especie'
    
    def __str__(self):
        """Representación en string de la especie."""
        return self.nombre


class Raza(models.Model):
    """
    Modelo que representa una raza de mascota.
    
    Las razas son subdivisiones específicas dentro de una especie.
    Cada raza pertenece a una especie específica y puede tener características
    particulares. Ejemplos: Golden Retriever (perro), Persa (gato), etc.
    
    Atributos:
        id_raza: Identificador único de la raza (clave primaria)
        id_especie: Referencia a la especie a la que pertenece
        nombre: Nombre de la raza
        activo: Indica si la raza está activa en el sistema
        fecha_registro: Fecha de registro en el sistema
        fecha_ultima_actualizacion: Fecha de última actualización
    """
    
    # Clave primaria
    id_raza = models.AutoField(primary_key=True)
    
    # Relación con especie
    id_especie = models.ForeignKey(Especie, models.DO_NOTHING, db_column='id_especie')
    
    # Datos de la raza
    nombre = models.CharField(max_length=100)
    
    # Estado y metadatos
    activo = models.BooleanField(blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)
    fecha_ultima_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Configuración del modelo."""
        managed = False
        db_table = 'raza'
    
    def __str__(self):
        """Representación en string de la raza."""
        return f"{self.nombre} ({self.id_especie.nombre})" 