"""
Modelos relacionados con las clínicas veterinarias del sistema.

Este módulo contiene los modelos para gestionar la información de las clínicas
veterinarias registradas, incluyendo sus datos de contacto, dirección,
relación con la comuna y los servicios que ofrecen.
"""

from django.db import models


class ClinicaVeterinaria(models.Model):
    """
    Modelo que representa una clínica veterinaria.
    
    Contiene toda la información relevante de una clínica veterinaria, incluyendo
    datos de contacto, dirección y la comuna en la que se encuentra ubicada.
    
    Atributos:
        id_clinica: Identificador único de la clínica (clave primaria)
        id_comuna: Referencia a la comuna donde está ubicada
        rut_clinica: RUT de la clínica (único)
        nombre: Nombre de la clínica
        razon_social: Razón social (opcional)
        email: Correo electrónico (opcional)
        telefono: Teléfono fijo (opcional)
        celular: Teléfono móvil (opcional)
        sitio_web: Sitio web (opcional)
        calle: Nombre de la calle (opcional)
        numero: Número de la dirección (opcional)
        complemento: Información adicional de la dirección (opcional)
        codigo_postal: Código postal (opcional)
        fecha_registro: Fecha de registro en el sistema (opcional)
        fecha_ultima_actualizacion: Fecha de última actualización (opcional)
    """
    
    # Clave primaria
    id_clinica = models.AutoField(primary_key=True)
    
    # Relación con comuna
    id_comuna = models.ForeignKey('Comuna', models.DO_NOTHING, db_column='id_comuna')
    
    # Datos de identificación y contacto
    rut_clinica = models.CharField(unique=True, max_length=15)
    nombre = models.CharField(max_length=100)
    razon_social = models.CharField(max_length=150, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    sitio_web = models.CharField(max_length=100, blank=True, null=True)
    
    # Dirección
    calle = models.CharField(max_length=100, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    
    # Metadatos
    fecha_registro = models.DateTimeField(blank=True, null=True)
    fecha_ultima_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Configuración del modelo."""
        managed = False
        db_table = 'clinica_veterinaria'
    
    def __str__(self):
        """Representación en string de la clínica veterinaria."""
        return self.nombre


class ClinicaServicio(models.Model):
    """
    Modelo de tabla intermedia entre ClinicaVeterinaria y ServicioDetalle.
    
    Permite establecer una relación muchos a muchos entre clínicas veterinarias
    y servicios detallados, donde una clínica puede ofrecer múltiples servicios
    y un servicio puede estar disponible en múltiples clínicas.
    
    Utiliza una clave primaria compuesta formada por id_clinica e id_servicio_detalle.
    
    Atributos:
        pk: Clave primaria compuesta (id_clinica, id_servicio_detalle)
        id_clinica: Referencia a la clínica veterinaria
        id_servicio_detalle: Referencia al servicio detallado
        costo_referencial: Costo referencial del servicio en la clínica (opcional)
        activo: Indica si el servicio está activo en la clínica (opcional)
        fecha_inicio: Fecha de inicio del servicio en la clínica (opcional)
        fecha_termino: Fecha de término del servicio en la clínica (opcional)
    """
    
    # Clave primaria compuesta
    pk = models.CompositePrimaryKey('id_clinica', 'id_servicio_detalle')
    
    # Relaciones
    id_clinica = models.ForeignKey(ClinicaVeterinaria, models.DO_NOTHING, db_column='id_clinica')
    id_servicio_detalle = models.ForeignKey('ServicioDetalle', models.DO_NOTHING, db_column='id_servicio_detalle')
    
    # Información del servicio en la clínica
    costo_referencial = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    activo = models.BooleanField(blank=True, null=True)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_termino = models.DateField(blank=True, null=True)

    class Meta:
        """Configuración del modelo."""
        managed = False
        db_table = 'clinica_servicio'
    
    def __str__(self):
        """Representación en string de la asociación clínica-servicio."""
        return f"{self.id_clinica} - {self.id_servicio_detalle}"