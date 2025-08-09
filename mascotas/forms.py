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
            'class': 'form-control',
            'id': 'id_raza'
        }),
        error_messages={
            'required': 'Debe seleccionar una raza.',
            'invalid_choice': 'La raza seleccionada no es válida.'
        }
    )
    
    color = forms.CharField(
        max_length=50,
        label='Color',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Color de la mascota'
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
    
    ESTADO_REPRODUCTIVO_CHOICES = [
        ('', 'Seleccione un estado'),
        ('Entero', 'Entero'),
        ('Esterilizado', 'Esterilizado'),
        ('Castrado', 'Castrado'),
    ]
    
    estado_reproductivo = forms.ChoiceField(
        choices=ESTADO_REPRODUCTIVO_CHOICES,
        label='Estado Reproductivo',
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
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

