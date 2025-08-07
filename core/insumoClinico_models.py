"""
Modelo relacionado con los insumos clínicos veterinarios.

Este módulo contiene el modelo para gestionar los insumos clínicos utilizados
en las atenciones veterinarias, incluyendo medicamentos, materiales y
equipos médicos.
"""

from django.db import models


class InsumoClinico(models.Model):
    """
    Modelo que representa un insumo clínico veterinario.
    
    Contiene la información de medicamentos, materiales y equipos médicos
    utilizados en las atenciones veterinarias, incluyendo datos de
    identificación, características técnicas y costos.
    
    Atributos:
        id_insumo: Identificador único del insumo (clave primaria)
        nombre: Nombre del insumo clínico
        tipo_insumo: Tipo o categoría del insumo (opcional)
        principio_activo: Principio activo del medicamento (opcional)
        laboratorio: Laboratorio fabricante (opcional)
        unidad_base: Unidad de medida base (opcional)
        precio_unitario: Precio unitario del insumo (opcional)
        activo: Indica si el insumo está activo en el sistema (opcional)
        fecha_registro: Fecha de registro en el sistema (opcional)
        fecha_ultima_actualizacion: Fecha de última actualización (opcional)
    """
    
    # Clave primaria
    id_insumo = models.AutoField(primary_key=True)
    
    # Información básica
    nombre = models.CharField(max_length=100)
    tipo_insumo = models.CharField(max_length=50, blank=True, null=True)
    
    # Características técnicas
    principio_activo = models.CharField(max_length=100, blank=True, null=True)
    laboratorio = models.CharField(max_length=100, blank=True, null=True)
    unidad_base = models.CharField(max_length=20, blank=True, null=True)
    
    # Información económica
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Estado y metadatos
    activo = models.BooleanField(blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)
    fecha_ultima_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Configuración del modelo."""
        managed = False
        db_table = 'insumo_clinico'
    
    def __str__(self):
        """Representación en string del insumo clínico."""
        return self.nombre 