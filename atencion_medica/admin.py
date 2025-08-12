"""
Admin para el módulo de atención médica.
"""

from django.contrib import admin
from .models import AtencionMedica, DocumentoAtencion


@admin.register(AtencionMedica)
class AtencionMedicaAdmin(admin.ModelAdmin):
    """
    Configuración del admin para AtencionMedica.
    """
    list_display = [
        'id_atencion', 'id_mascota', 'id_clinica', 'id_personal', 
        'fecha_atencion', 'estado', 'fecha_registro'
    ]
    list_filter = ['estado', 'fecha_atencion', 'id_clinica', 'id_personal']
    search_fields = [
        'id_mascota__nombre', 'id_mascota__nro_chip', 
        'id_personal__nombres', 'id_personal__apellido_paterno',
        'motivo_atencion', 'diagnostico'
    ]
    readonly_fields = ['fecha_registro', 'fecha_actualizacion']
    date_hierarchy = 'fecha_atencion'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('id_mascota', 'id_clinica', 'id_personal', 'id_servicio_detalle', 'estado')
        }),
        ('Fecha y Datos Clínicos', {
            'fields': ('fecha_atencion', 'peso', 'temperatura')
        }),
        ('Información Médica', {
            'fields': ('motivo_atencion', 'detalle_clinico', 'diagnostico', 'tratamiento')
        }),
        ('Fechas del Sistema', {
            'fields': ('fecha_registro', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DocumentoAtencion)
class DocumentoAtencionAdmin(admin.ModelAdmin):
    """
    Configuración del admin para DocumentoAtencion.
    """
    list_display = [
        'id_documento', 'id_atencion', 'tipo_documento', 
        'nombre_archivo', 'fecha_subida'
    ]
    list_filter = ['tipo_documento', 'fecha_subida']
    search_fields = [
        'id_atencion__id_atencion', 'nombre_archivo', 
        'id_atencion__id_mascota__nombre'
    ]
    readonly_fields = ['fecha_subida']
    date_hierarchy = 'fecha_subida'
