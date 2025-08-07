"""
Modelos relacionados con las recetas médicas veterinarias.

Este módulo contiene los modelos para gestionar las recetas médicas,
incluyendo la información general de la receta y los items específicos
que la componen. Los modelos están organizados jerárquicamente:
Receta -> RecetaItem.
"""

from django.db import models


class Receta(models.Model):
    """
    Modelo que representa una receta médica veterinaria.
    
    Contiene la información general de una receta emitida durante una
    atención clínica, incluyendo tipo de receta, fecha de emisión e
    indicaciones generales.
    
    Atributos:
        id_receta: Identificador único de la receta (clave primaria)
        id_atencion: Referencia única a la atención clínica asociada
        tipo_receta: Tipo o categoría de la receta (opcional)
        fecha_emision: Fecha de emisión de la receta (opcional)
        indicaciones_generales: Indicaciones generales del tratamiento (opcional)
        fecha_registro: Fecha de registro en el sistema (opcional)
        fecha_ultima_actualizacion: Fecha de última actualización (opcional)
    """
    
    # Clave primaria
    id_receta = models.AutoField(primary_key=True)
    
    # Relación con atención (uno a uno)
    id_atencion = models.OneToOneField('AtencionClinica', models.DO_NOTHING, db_column='id_atencion')
    
    # Información de la receta
    tipo_receta = models.CharField(max_length=50, blank=True, null=True)
    fecha_emision = models.DateField(blank=True, null=True)
    indicaciones_generales = models.TextField(blank=True, null=True)
    
    # Metadatos
    fecha_registro = models.DateTimeField(blank=True, null=True)
    fecha_ultima_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Configuración del modelo."""
        managed = False
        db_table = 'receta'
    
    def __str__(self):
        """Representación en string de la receta."""
        return f"Receta {self.id_receta} - {self.id_atencion} ({self.fecha_emision})"


class RecetaItem(models.Model):
    """
    Modelo que representa un item específico de una receta médica.
    
    Contiene la información detallada de cada medicamento o tratamiento
    prescrito en una receta, incluyendo dosis, frecuencia, duración y
    vía de administración.
    
    Atributos:
        id_receta_item: Identificador único del item de receta (clave primaria)
        id_receta: Referencia a la receta a la que pertenece
        tipo_item: Tipo o categoría del item (opcional)
        nombre_item: Nombre del medicamento o tratamiento (opcional)
        dosis: Dosis prescrita (opcional)
        frecuencia: Frecuencia de administración (opcional)
        duracion: Duración del tratamiento (opcional)
        via_administracion: Vía de administración (opcional)
        observaciones: Observaciones adicionales (opcional)
        recomendado_en: Momento recomendado para la administración (opcional)
    """
    
    # Clave primaria
    id_receta_item = models.AutoField(primary_key=True)
    
    # Relación con receta
    id_receta = models.ForeignKey(Receta, models.DO_NOTHING, db_column='id_receta')
    
    # Información del item
    tipo_item = models.CharField(max_length=50, blank=True, null=True)
    nombre_item = models.CharField(max_length=100, blank=True, null=True)
    
    # Detalles de administración
    dosis = models.CharField(max_length=50, blank=True, null=True)
    frecuencia = models.CharField(max_length=50, blank=True, null=True)
    duracion = models.CharField(max_length=50, blank=True, null=True)
    via_administracion = models.CharField(max_length=50, blank=True, null=True)
    
    # Información adicional
    observaciones = models.TextField(blank=True, null=True)
    recomendado_en = models.TextField(blank=True, null=True)

    class Meta:
        """Configuración del modelo."""
        managed = False
        db_table = 'receta_item'
    
    def __str__(self):
        """Representación en string del item de receta."""
        if self.nombre_item:
            return f"{self.nombre_item} - {self.id_receta}"
        else:
            return f"Item {self.id_receta_item} - {self.id_receta}" 