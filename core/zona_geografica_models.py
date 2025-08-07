"""
Modelos relacionados con la división geográfica de Chile.

Este módulo contiene los modelos para gestionar la información geográfica
del país, incluyendo regiones, provincias y comunas. Los modelos están
organizados jerárquicamente: Region -> Provincia -> Comuna.
"""

from django.db import models


class Region(models.Model):
    """
    Modelo que representa una región de Chile.
    
    Las regiones son la división administrativa de mayor nivel en Chile.
    Cada región puede contener múltiples provincias.
    
    Atributos:
        id_region: Identificador único de la región (clave primaria)
        region: Nombre de la región
        fecha_registro: Fecha de registro en el sistema
        fecha_ultima_actualizacion: Fecha de última actualización
    """
    
    # Clave primaria
    id_region = models.AutoField(primary_key=True)
    
    # Datos de la región
    region = models.CharField(max_length=100)
    
    # Metadatos
    fecha_registro = models.DateTimeField(blank=True, null=True)
    fecha_ultima_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Configuración del modelo."""
        managed = False
        db_table = 'region'
    
    def __str__(self):
        """Representación en string de la región."""
        return self.region


class Provincia(models.Model):
    """
    Modelo que representa una provincia de Chile.
    
    Las provincias son divisiones administrativas intermedias que pertenecen
    a una región. Cada provincia puede contener múltiples comunas.
    
    Atributos:
        id_provincia: Identificador único de la provincia (clave primaria)
        id_region: Referencia a la región a la que pertenece
        provincia: Nombre de la provincia
        fecha_registro: Fecha de registro en el sistema
        fecha_ultima_actualizacion: Fecha de última actualización
    """
    
    # Clave primaria
    id_provincia = models.AutoField(primary_key=True)
    
    # Relación con región
    id_region = models.ForeignKey(Region, models.DO_NOTHING, db_column='id_region')
    
    # Datos de la provincia
    provincia = models.CharField(max_length=100)
    
    # Metadatos
    fecha_registro = models.DateTimeField(blank=True, null=True)
    fecha_ultima_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Configuración del modelo."""
        managed = False
        db_table = 'provincia'
    
    def __str__(self):
        """Representación en string de la provincia."""
        return self.provincia


class Comuna(models.Model):
    """
    Modelo que representa una comuna de Chile.
    
    Las comunas son las divisiones administrativas de menor nivel en Chile.
    Cada comuna pertenece a una provincia específica. Las comunas son utilizadas
    para ubicar direcciones de tutores, clínicas veterinarias y otros establecimientos.
    
    Atributos:
        id_comuna: Identificador único de la comuna (clave primaria)
        id_provincia: Referencia a la provincia a la que pertenece
        comuna: Nombre de la comuna
        fecha_registro: Fecha de registro en el sistema
        fecha_ultima_actualizacion: Fecha de última actualización
    """
    
    # Clave primaria
    id_comuna = models.AutoField(primary_key=True)
    
    # Relación con provincia
    id_provincia = models.ForeignKey(Provincia, models.DO_NOTHING, db_column='id_provincia')
    
    # Datos de la comuna
    comuna = models.CharField(max_length=100)
    
    # Metadatos
    fecha_registro = models.DateTimeField(blank=True, null=True)
    fecha_ultima_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Configuración del modelo."""
        managed = False
        db_table = 'comuna'
    
    def __str__(self):
        """Representación en string de la comuna."""
        return self.comuna 