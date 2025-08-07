"""
Modelos relacionados con los servicios veterinarios del sistema.

Este módulo contiene los modelos para gestionar la información de los servicios
veterinarios, incluyendo servicios generales y sus detalles específicos.
Los modelos están organizados jerárquicamente: Servicio -> ServicioDetalle.
"""

from django.db import models


class Servicio(models.Model):
    """
    Modelo que representa un servicio veterinario general.
    
    Los servicios son categorías generales de atención veterinaria que pueden
    contener múltiples detalles específicos. Ejemplos: Consulta, Cirugía,
    Vacunación, etc.
    
    Atributos:
        id_servicio: Identificador único del servicio (clave primaria)
        nombre: Nombre del servicio
        descripcion: Descripción detallada del servicio (opcional)
        tipo_servicio: Tipo o categoría del servicio (opcional)
        activo: Indica si el servicio está activo en el sistema (opcional)
        fecha_registro: Fecha de registro en el sistema (opcional)
        fecha_ultima_actualizacion: Fecha de última actualización (opcional)
    """
    
    # Clave primaria
    id_servicio = models.AutoField(primary_key=True)
    
    # Datos del servicio
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    tipo_servicio = models.CharField(max_length=50, blank=True, null=True)
    
    # Estado y metadatos
    activo = models.BooleanField(blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)
    fecha_ultima_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Configuración del modelo."""
        managed = False
        db_table = 'servicio'
    
    def __str__(self):
        """Representación en string del servicio."""
        return self.nombre


class ServicioDetalle(models.Model):
    """
    Modelo que representa un detalle específico de un servicio veterinario.
    
    Los detalles de servicio son subdivisiones específicas dentro de un servicio
    general. Cada detalle pertenece a un servicio específico y puede tener
    características particulares. Ejemplos: Consulta de urgencia, Cirugía menor,
    Vacuna antirrábica, etc.
    
    Atributos:
        id_servicio_detalle: Identificador único del detalle de servicio (clave primaria)
        id_servicio: Referencia al servicio al que pertenece
        nombre: Nombre del detalle de servicio
        activo: Indica si el detalle está activo en el sistema (opcional)
        fecha_registro: Fecha de registro en el sistema (opcional)
        fecha_ultima_actualizacion: Fecha de última actualización (opcional)
    """
    
    # Clave primaria
    id_servicio_detalle = models.AutoField(primary_key=True)
    
    # Relación con servicio
    id_servicio = models.ForeignKey(Servicio, models.DO_NOTHING, db_column='id_servicio')
    
    # Datos del detalle de servicio
    nombre = models.CharField(max_length=100)
    
    # Estado y metadatos
    activo = models.BooleanField(blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)
    fecha_ultima_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Configuración del modelo."""
        managed = False
        db_table = 'servicio_detalle'
    
    def __str__(self):
        """Representación en string del detalle de servicio."""
        return f"{self.nombre} ({self.id_servicio.nombre})" 