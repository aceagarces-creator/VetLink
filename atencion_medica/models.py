"""
Modelos para el módulo de atención médica.
"""

from django.db import models
from core.models import Mascota, PersonalClinica, ServicioDetalle, ClinicaVeterinaria


class AtencionMedica(models.Model):
    """
    Modelo para registrar atenciones médicas de mascotas.
    """
    TIPOS_ESTADO = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROCESO', 'En Proceso'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    ]

    id_atencion = models.AutoField(primary_key=True)
    id_mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, db_column='id_mascota')
    id_clinica = models.ForeignKey(ClinicaVeterinaria, on_delete=models.CASCADE, db_column='id_clinica')
    id_personal = models.ForeignKey(PersonalClinica, on_delete=models.CASCADE, db_column='id_personal')
    id_servicio_detalle = models.ForeignKey(ServicioDetalle, on_delete=models.CASCADE, db_column='id_servicio_detalle')
    
    fecha_atencion = models.DateField()
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temperatura = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    motivo_atencion = models.TextField()
    detalle_clinico = models.TextField()
    diagnostico = models.TextField()
    tratamiento = models.TextField()
    
    estado = models.CharField(max_length=20, choices=TIPOS_ESTADO, default='PENDIENTE')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'atencion_medica'
        verbose_name = 'Atención Médica'
        verbose_name_plural = 'Atenciones Médicas'
        ordering = ['-fecha_atencion', '-fecha_registro']

    def __str__(self):
        return f"Atención {self.id_atencion} - {self.id_mascota.nombre} - {self.fecha_atencion}"


class DocumentoAtencion(models.Model):
    """
    Modelo para documentos adjuntos a atenciones médicas.
    """
    TIPOS_DOCUMENTO = [
        ('RADIOGRAFIA', 'Radiografía'),
        ('ANALISIS_SANGRE', 'Análisis de Sangre'),
        ('ECOGRAFIA', 'Ecografía'),
        ('HISTORIA_CLINICA', 'Historia Clínica'),
        ('RECETA', 'Receta'),
        ('CERTIFICADO', 'Certificado'),
        ('OTRO', 'Otro'),
    ]

    id_documento = models.AutoField(primary_key=True)
    id_atencion = models.ForeignKey(AtencionMedica, on_delete=models.CASCADE, db_column='id_atencion')
    tipo_documento = models.CharField(max_length=20, choices=TIPOS_DOCUMENTO)
    nombre_archivo = models.CharField(max_length=255)
    archivo = models.FileField(upload_to='documentos_atencion/')
    fecha_subida = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'documento_atencion'
        verbose_name = 'Documento de Atención'
        verbose_name_plural = 'Documentos de Atención'
        ordering = ['-fecha_subida']

    def __str__(self):
        return f"{self.get_tipo_documento_display()} - {self.nombre_archivo}"
