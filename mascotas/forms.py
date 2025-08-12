"""
Formularios para la gestión de mascotas.

Este módulo contiene los formularios utilizados para la gestión de mascotas,
incluyendo registro y búsqueda de tutores para asociar mascotas.
"""

from django import forms
from django.core.exceptions import ValidationError
from core.models import Tutor, Mascota, Especie, Raza
import re
from datetime import date


class BuscarTutorMascotaForm(forms.Form):
    """
    Formulario para buscar un tutor por RUT (con dígito verificador).
    """
    rut_tutor = forms.CharField(
        max_length=10,
        label='Ingrese el Rut del tutor',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 15468064-0',
            'style': 'max-width: 250px;',
            'pattern': '[0-9Kk-]*',
            'oninput': 'this.value = this.value.replace(/[^0-9Kk-]/g, "").replace(/k/g, "K");'
        }),
        help_text='Ingrese el RUT con formato: 15468064-0 (7-8 dígitos, guión y dígito verificador)'
    )

    def clean_rut_tutor(self):
        rut_tutor = self.cleaned_data['rut_tutor']
        
        # Limpiar el RUT: solo permitir números, guión y K
        rut_limpio = ''.join(c for c in rut_tutor if c.isdigit() or c == '-' or c.upper() == 'K')
        
        # Convertir k minúscula a K mayúscula
        rut_limpio = rut_limpio.replace('k', 'K')
        
        # Validar que contenga al menos un guión
        if '-' not in rut_limpio:
            raise forms.ValidationError('El RUT debe contener un guión (-) para separar el número del dígito verificador')
        
        # Validar formato del RUT
        if not re.match(r'^\d{7,8}-[0-9K]$', rut_limpio):
            raise forms.ValidationError('El RUT debe tener el formato: 15468064-0 (7-8 dígitos, guión y dígito verificador)')
        
        # Validar dígito verificador
        numero = rut_limpio.split('-')[0]
        dv = rut_limpio.split('-')[1]
        
        suma = 0
        multiplicador = 2
        
        for digito in reversed(numero):
            suma += int(digito) * multiplicador
            multiplicador = multiplicador + 1 if multiplicador < 7 else 2
        
        dv_calculado = 11 - (suma % 11)
        if dv_calculado == 11:
            dv_calculado = '0'
        elif dv_calculado == 10:
            dv_calculado = 'K'
        else:
            dv_calculado = str(dv_calculado)
        
        if dv.upper() != dv_calculado:
            raise forms.ValidationError('El dígito verificador del RUT no es válido. Verifique el número ingresado.')
        
        return rut_limpio


class RegistrarMascotaForm(forms.Form):
    """
    Formulario para registrar una nueva mascota.
    """
    
    # Datos básicos de la mascota
    nombre = forms.CharField(
        max_length=100,
        label='Nombre (*)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de la mascota'
        }),
        error_messages={
            'required': 'El nombre de la mascota es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        }
    )
    
    especie = forms.ModelChoiceField(
        queryset=Especie.objects.filter(activo=True),
        label='Especie (*)',
        empty_label='Seleccione una especie',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_especie'
        }),
        error_messages={
            'required': 'Debe seleccionar una especie.',
            'invalid_choice': 'La especie seleccionada no es válida.'
        }
    )
    
    raza = forms.ModelChoiceField(
        queryset=Raza.objects.none(),  # Se carga dinámicamente
        label='Raza (*)',
        empty_label='Primero seleccione una especie',
        widget=forms.Select(attrs={
            'class': 'form-control select2-enabled',
            'id': 'id_raza',
            'data-placeholder': 'Seleccione una raza'
        }),
        error_messages={
            'required': 'Debe seleccionar una raza.',
            'invalid_choice': 'La raza seleccionada no es válida.'
        }
    )
    
    COLOR_CHOICES = [
        ('', 'Seleccione un color'),
        ('AMARILLO', 'AMARILLO'),
        ('AMARILLO-BLANCO', 'AMARILLO-BLANCO'),
        ('AMARILLO-CAFÉ', 'AMARILLO-CAFÉ'),
        ('AMARILLO-CAFÉ-ROJO', 'AMARILLO-CAFÉ-ROJO'),
        ('AMARILLO-NEGRO', 'AMARILLO-NEGRO'),
        ('AMARILLO-NEGRO-CAFÉ', 'AMARILLO-NEGRO-CAFÉ'),
        ('AMARILLO-ROJO', 'AMARILLO-ROJO'),
        ('AZUL', 'AZUL'),
        ('BLANCO', 'BLANCO'),
        ('BLANCO-AMARILLO', 'BLANCO-AMARILLO'),
        ('BLANCO-AMARILLO-CAFÉ', 'BLANCO-AMARILLO-CAFÉ'),
        ('BLANCO-AMARILLO-NEGRO', 'BLANCO-AMARILLO-NEGRO'),
        ('BLANCO-AMARILLO-ROJO', 'BLANCO-AMARILLO-ROJO'),
        ('BLANCO-CAFÉ', 'BLANCO-CAFÉ'),
        ('BLANCO-CAFÉ-NEGRO', 'BLANCO-CAFÉ-NEGRO'),
        ('BLANCO-CAFÉ-ROJO', 'BLANCO-CAFÉ-ROJO'),
        ('BLANCO-CREMA', 'BLANCO-CREMA'),
        ('BLANCO-CREMA-AMARILLO', 'BLANCO-CREMA-AMARILLO'),
        ('BLANCO-CREMA-CAFÉ', 'BLANCO-CREMA-CAFÉ'),
        ('BLANCO-CREMA-ROJO', 'BLANCO-CREMA-ROJO'),
        ('BLANCO-GRIS', 'BLANCO-GRIS'),
        ('BLANCO-GRIS-AMARILLO', 'BLANCO-GRIS-AMARILLO'),
        ('BLANCO-GRIS-CAFÉ', 'BLANCO-GRIS-CAFÉ'),
        ('BLANCO-GRIS-CREMA', 'BLANCO-GRIS-CREMA'),
        ('BLANCO-GRIS-ROJO', 'BLANCO-GRIS-ROJO'),
        ('BLANCO-NARANJA', 'BLANCO-NARANJA'),
        ('BLANCO-NEGRO', 'BLANCO-NEGRO'),
        ('BLANCO-NEGRO-AMARILLO', 'BLANCO-NEGRO-AMARILLO'),
        ('BLANCO-NEGRO-CAFE', 'BLANCO-NEGRO-CAFE'),
        ('BLANCO-NEGRO-CREMA', 'BLANCO-NEGRO-CREMA'),
        ('BLANCO-NEGRO-GRIS', 'BLANCO-NEGRO-GRIS'),
        ('BLANCO-NEGRO-ROJO', 'BLANCO-NEGRO-ROJO'),
        ('BLANCO-ROJO', 'BLANCO-ROJO'),
        ('CAFÉ', 'CAFÉ'),
        ('CAFÉ-BLANCO', 'CAFÉ-BLANCO'),
        ('CAFÉ-GRIS-BLANCO', 'CAFÉ-GRIS-BLANCO'),
        ('CAFÉ-NEGRO-GRIS', 'CAFÉ-NEGRO-GRIS'),
        ('CAFÉ-ROJO', 'CAFÉ-ROJO'),
        ('CREMA', 'CREMA'),
        ('CREMA-AMARILLO', 'CREMA-AMARILLO'),
        ('CREMA-AMARILLO-CAFÉ', 'CREMA-AMARILLO-CAFÉ'),
        ('CREMA-AMARILLO-ROJO', 'CREMA-AMARILLO-ROJO'),
        ('CREMA-CAFÉ', 'CREMA-CAFÉ'),
        ('CREMA-CAFÉ-ROJO', 'CREMA-CAFÉ-ROJO'),
        ('CREMA-ROJO', 'CREMA-ROJO'),
        ('GRIS', 'GRIS'),
        ('GRIS-AMARILLO', 'GRIS-AMARILLO'),
        ('GRIS-AMARILLO-CAFÉ', 'GRIS-AMARILLO-CAFÉ'),
        ('GRIS-AMARILLO-ROJO', 'GRIS-AMARILLO-ROJO'),
        ('GRIS-BLANCO', 'GRIS-BLANCO'),
        ('GRIS-CAFÉ', 'GRIS-CAFÉ'),
        ('GRIS-CAFÉ-ROJO', 'GRIS-CAFÉ-ROJO'),
        ('GRIS-CREMA', 'GRIS-CREMA'),
        ('GRIS-CREMA-AMARILLO', 'GRIS-CREMA-AMARILLO'),
        ('GRIS-CREMA-CAFÉ', 'GRIS-CREMA-CAFÉ'),
        ('GRIS-CREMA-ROJO', 'GRIS-CREMA-ROJO'),
        ('GRIS-ROJO', 'GRIS-ROJO'),
        ('NARANJA', 'NARANJA'),
        ('NEGRO', 'NEGRO'),
        ('NEGRO-AMARILLO', 'NEGRO-AMARILLO'),
        ('NEGRO-AMARILLO-CAFÉ', 'NEGRO-AMARILLO-CAFÉ'),
        ('NEGRO-AMARILLO-ROJO', 'NEGRO-AMARILLO-ROJO'),
        ('NEGRO-BLANCO', 'NEGRO-BLANCO'),
        ('NEGRO-CAFÉ', 'NEGRO-CAFÉ'),
        ('NEGRO-CREMA', 'NEGRO-CREMA'),
        ('NEGRO-CREMA-AMARILLO', 'NEGRO-CREMA-AMARILLO'),
        ('NEGRO-CREMA-CAFÉ', 'NEGRO-CREMA-CAFÉ'),
        ('NEGRO-CREMA-ROJO', 'NEGRO-CREMA-ROJO'),
        ('NEGRO-GRIS', 'NEGRO-GRIS'),
        ('NEGRO-GRIS-AMARILLO', 'NEGRO-GRIS-AMARILLO'),
        ('NEGRO-GRIS-CAFÉ', 'NEGRO-GRIS-CAFÉ'),
        ('NEGRO-GRIS-CREMA', 'NEGRO-GRIS-CREMA'),
        ('NEGRO-GRIS-NARANJA', 'NEGRO-GRIS-NARANJA'),
        ('NEGRO-GRIS-ROJO', 'NEGRO-GRIS-ROJO'),
        ('NEGRO-ROJO', 'NEGRO-ROJO'),
        ('ROJO', 'ROJO'),
    ]
    
    color = forms.ChoiceField(
        choices=COLOR_CHOICES,
        label='Color',
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control select2-enabled',
            'id': 'id_color',
            'data-placeholder': 'Seleccione un color'
        })
    )
    
    PATRON_CHOICES = [
        ('', 'Seleccione un patrón'),
        ('BANDAS O FRANJAS', 'BANDAS O FRANJAS'),
        ('JASPEADO', 'JASPEADO'),
        ('MANCHAS/PARCHES', 'MANCHAS/PARCHES'),
        ('NINGUNO', 'NINGUNO'),
        ('NO SE SEÑALA', 'NO SE SEÑALA'),
        ('PUNTAS DE OTRO COLOR', 'PUNTAS DE OTRO COLOR'),
        ('RAYAS/ATIGRADO', 'RAYAS/ATIGRADO'),
        ('SOMBREADO/LEONADO', 'SOMBREADO/LEONADO'),
    ]
    
    patron = forms.ChoiceField(
        choices=PATRON_CHOICES,
        label='Patrón',
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control select2-enabled',
            'id': 'id_patron',
            'data-placeholder': 'Seleccione un patrón'
        })
    )
    
    nro_chip = forms.CharField(
        max_length=30,
        label='Número de Chip (*)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el número de chip único de identificación'
        }),
        error_messages={
            'required': 'El número de chip es obligatorio.',
            'max_length': 'El número de chip no puede tener más de 30 caracteres.'
        }
    )
    
    SEXO_CHOICES = [
        ('', 'Seleccione un sexo (*)'),
        ('Macho', 'Macho'),
        ('Hembra', 'Hembra'),
    ]
    
    sexo = forms.ChoiceField(
        choices=SEXO_CHOICES,
        label='Sexo (*)',
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        error_messages={
            'required': 'Debe seleccionar el sexo de la mascota.',
            'invalid_choice': 'La opción de sexo seleccionada no es válida.'
        }
    )
    
    fecha_nacimiento = forms.DateField(
        label='Fecha de Nacimiento',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        error_messages={
            'invalid': 'La fecha de nacimiento no tiene un formato válido.'
        }
    )
    
    ESTERILIZADO_CHOICES = [
        ('True', 'Si'),
        ('False', 'No'),
    ]
    
    estado_reproductivo = forms.ChoiceField(
        choices=ESTERILIZADO_CHOICES,
        label='Esterilizado',
        required=False,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        help_text='Seleccione si la mascota está esterilizada'
    )
    
    MODO_OBTENCION_CHOICES = [
        ('', 'Seleccione...'),
        ('compra', 'Compra'),
        ('regalo', 'Regalo'),
        ('nacido_en_casa', 'Nacido en casa'),
        ('adopcion_reubicacion', 'Adopción o Reubicación'),
        ('recogido', 'Recogido'),
    ]
    
    modo_obtencion = forms.ChoiceField(
        choices=MODO_OBTENCION_CHOICES,
        label='Modo de Obtención',
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'width: 100%; padding: 8px 12px; border: 1px solid #ccc; border-radius: 4px; background-color: white; color: #333; box-sizing: border-box; font-size: 0.7rem;'
        })
    )
    
    RAZON_TENENCIA_CHOICES = [
        ('', 'Seleccione...'),
        ('asistencia', 'Asistencia'),
        ('caza', 'Caza'),
        ('compania', 'Compañía'),
        ('deporte', 'Deporte'),
        ('exposicion', 'Exposición'),
        ('otro', 'Otro'),
        ('reproduccion', 'Reproducción'),
        ('seguridad', 'Seguridad'),
        ('terapia', 'Terapia'),
        ('trabajo', 'Trabajo'),
    ]
    
    razon_tenencia = forms.ChoiceField(
        choices=RAZON_TENENCIA_CHOICES,
        label='Razón de Tenencia',
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'width: 100%; padding: 8px 12px; border: 1px solid #ccc; border-radius: 4px; background-color: white; color: #333; box-sizing: border-box; font-size: 0.7rem;'
        })
    )
    
    notas_adicionales = forms.CharField(
        label='Notas Adicionales',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Información adicional sobre la mascota'
        })
    )
    
    documento_consentimiento = forms.FileField(
        label='Documento de Consentimiento',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.jpg,.jpeg,.png'
        }),
        error_messages={
            'invalid': 'El archivo seleccionado no es válido.'
        }
    )
    
    # Campo oculto para el ID del tutor
    tutor_id = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )


class BuscarFichaClinicaForm(forms.Form):
    """
    Formulario para buscar una mascota por número de chip para mostrar su ficha clínica.
    Solo para consultas - no valida unicidad.
    """
    nro_chip = forms.CharField(
        max_length=30,
        label='Número de Chip',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el número de chip de la mascota',
            'style': 'max-width: 300px;'
        }),
        help_text='Ingrese el número de chip único de identificación de la mascota'
    )

    def clean_nro_chip(self):
        nro_chip = self.cleaned_data['nro_chip']
        
        # Normalizar el valor: recortar espacios en blanco pero conservar ceros a la izquierda
        nro_chip = nro_chip.strip()
        
        if not nro_chip:
            raise forms.ValidationError('El número de chip es obligatorio')
        
        # Solo normalizar, sin validar existencia (esto es para consultas, no para registro)
        return nro_chip

