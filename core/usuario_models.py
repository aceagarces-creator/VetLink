"""
Modelo relacionado con los usuarios del sistema veterinario.

Este módulo contiene el modelo para gestionar las cuentas de usuario del sistema,
incluyendo autenticación, roles y sesiones de los miembros del personal.
"""

from django.db import models


class Usuario(models.Model):
    """
    Modelo que representa una cuenta de usuario del sistema veterinario.
    
    Los usuarios son cuentas de acceso al sistema que están asociadas a un
    miembro del personal de una clínica. Permiten autenticación, control de
    acceso y seguimiento de sesiones.
    
    Atributos:
        id_usuario: Identificador único del usuario (clave primaria)
        id_personal: Referencia al personal de clínica asociado
        email: Correo electrónico único del usuario
        password_hash: Hash de la contraseña del usuario
        activo: Indica si la cuenta está activa (opcional)
        rol: Rol o nivel de acceso del usuario en el sistema
        fecha_creacion: Fecha de creación de la cuenta (opcional)
        fecha_ultima_sesion: Fecha de la última sesión iniciada (opcional)
    """
    
    # Clave primaria
    id_usuario = models.AutoField(primary_key=True)
    
    # Relación con personal
    id_personal = models.ForeignKey('PersonalClinica', models.DO_NOTHING, db_column='id_personal')
    
    # Datos de autenticación
    email = models.CharField(unique=True, max_length=100)
    password_hash = models.TextField()
    
    # Estado y permisos
    activo = models.BooleanField(blank=True, null=True)
    rol = models.CharField(max_length=50)
    
    # Metadatos de sesión
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    fecha_ultima_sesion = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Configuración del modelo."""
        managed = False
        db_table = 'usuario'
    
    def __str__(self):
        """Representación en string del usuario."""
        return f"{self.email} ({self.id_personal})" 