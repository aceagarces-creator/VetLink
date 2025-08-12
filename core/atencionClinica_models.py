"""
Modelos relacionados con la atención clínica veterinaria.

Este módulo contiene los modelos para gestionar las atenciones clínicas,
incluyendo la información de la consulta, insumos utilizados y documentos
adjuntos. Los modelos están organizados jerárquicamente:
AtencionClinica -> AtencionInsumo/DocumentoAdjunto.
"""

from django.db import models


class AtencionClinica(models.Model):
    """
    Modelo que representa una atención clínica veterinaria.
    
    Contiene toda la información relevante de una consulta o atención
    veterinaria, incluyendo datos del paciente, personal médico,
    servicio prestado y detalles clínicos.
    
    Atributos:
        id_atencion: Identificador único de la atención (clave primaria)
        id_mascota: Referencia a la mascota atendida
        id_clinica: Referencia a la clínica donde se realizó la atención
        id_personal: Referencia al personal médico que realizó la atención
        id_servicio_detalle: Referencia al servicio específico prestado
        fecha_atencion: Fecha y hora de la atención
        peso_kg: Peso de la mascota en kilogramos (opcional)
        temperatura_c: Temperatura corporal en grados Celsius (opcional)
        motivo: Motivo de la consulta (opcional)
        detalle_clinico: Detalles clínicos de la atención (opcional)
        diagnostico: Diagnóstico realizado (opcional)
        tratamiento: Tratamiento aplicado (opcional)
        fecha_registro: Fecha de registro en el sistema (opcional)
        fecha_ultima_actualizacion: Fecha de última actualización (opcional)
    """
    
    # Clave primaria
    id_atencion = models.AutoField(primary_key=True)
    
    # Relaciones principales
    id_mascota = models.ForeignKey('Mascota', models.DO_NOTHING, db_column='id_mascota')
    id_clinica = models.ForeignKey('ClinicaVeterinaria', models.DO_NOTHING, db_column='id_clinica')
    id_personal = models.ForeignKey('PersonalClinica', models.DO_NOTHING, db_column='id_personal')
    id_servicio_detalle = models.ForeignKey('ServicioDetalle', models.DO_NOTHING, db_column='id_servicio_detalle')
    
    # Información temporal
    fecha_atencion = models.DateTimeField()
    
    # Signos vitales
    peso_kg = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    temperatura_c = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    
    # Información clínica
    motivo = models.TextField(blank=True, null=True)
    detalle_clinico = models.TextField(blank=True, null=True)
    diagnostico = models.TextField(blank=True, null=True)
    tratamiento = models.TextField(blank=True, null=True)
    
    # Metadatos
    fecha_registro = models.DateTimeField(blank=True, null=True)
    fecha_ultima_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Configuración del modelo."""
        managed = False
        db_table = 'atencion_clinica'
    
    def __str__(self):
        """Representación en string de la atención clínica."""
        return f"Atención {self.id_atencion} - {self.id_mascota} ({self.fecha_atencion})"


class AtencionInsumo(models.Model):
    """
    Modelo de tabla intermedia entre AtencionClinica e InsumoClinico.
    
    Permite registrar los insumos clínicos utilizados en una atención
    específica, incluyendo cantidades, costos y detalles de administración.
    
    Utiliza una clave primaria compuesta formada por id_atencion e id_insumo.
    
    Atributos:
        id_atencion: Referencia a la atención clínica
        id_insumo: Referencia al insumo clínico utilizado
        cantidad_utilizada: Cantidad del insumo utilizada (opcional)
        costo_asociado: Costo asociado al uso del insumo (opcional)
        dosis: Dosis administrada (opcional)
        via_administracion: Vía de administración del insumo (opcional)
        observaciones: Observaciones adicionales (opcional)
        fecha_registro: Fecha de registro del uso (opcional)
    """
    
    # Relaciones (clave primaria compuesta se maneja en Meta)
    id_atencion = models.ForeignKey(AtencionClinica, models.DO_NOTHING, db_column='id_atencion')
    id_insumo = models.ForeignKey('InsumoClinico', models.DO_NOTHING, db_column='id_insumo')
    
    # Información de uso
    cantidad_utilizada = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    costo_asociado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Detalles de administración
    dosis = models.CharField(max_length=100, blank=True, null=True)
    via_administracion = models.CharField(max_length=100, blank=True, null=True)
    
    # Información adicional
    observaciones = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Configuración del modelo."""
        managed = False
        db_table = 'atencion_insumo'
        unique_together = [['id_atencion', 'id_insumo']]
    
    def __str__(self):
        """Representación en string de la asociación atención-insumo."""
        return f"{self.id_atencion} - {self.id_insumo}"


class DocumentoAdjunto(models.Model):
    """
    Modelo que representa documentos adjuntos a una atención clínica.
    
    Permite almacenar información sobre documentos digitales relacionados
    con una atención específica, como radiografías, análisis de laboratorio,
    certificados, etc.
    
    Atributos:
        id_documento: Identificador único del documento (clave primaria)
        id_atencion: Referencia a la atención clínica asociada
        tipo_documento: Tipo o categoría del documento (opcional)
        nombre_archivo: Nombre original del archivo (opcional)
        url_archivo: URL o ruta del archivo almacenado (opcional)
        fecha_subida: Fecha de subida del documento (opcional)
        observaciones: Observaciones sobre el documento (opcional)
    """
    
    # Clave primaria
    id_documento = models.AutoField(primary_key=True)
    
    # Relación con atención
    id_atencion = models.ForeignKey(AtencionClinica, models.DO_NOTHING, db_column='id_atencion')
    
    # Información del documento
    tipo_documento = models.CharField(max_length=50, blank=True, null=True)
    nombre_archivo = models.CharField(max_length=255, blank=True, null=True)
    url_archivo = models.TextField(blank=True, null=True)
    
    # Metadatos
    fecha_subida = models.DateTimeField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        """Configuración del modelo."""
        managed = False
        db_table = 'documento_adjunto'
    
    def __str__(self):
        """Representación en string del documento adjunto."""
        if self.nombre_archivo:
            return f"{self.nombre_archivo} ({self.id_atencion})"
        else:
            return f"Documento {self.id_documento} ({self.id_atencion})" 