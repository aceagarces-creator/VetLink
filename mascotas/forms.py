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
    Formulario para buscar un tutor por RUT (sin dígito verificador).
    """
    rut_tutor = forms.CharField(
        max_length=8,
        label='RUT del Tutor (sin dígito verificador)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 15468064',
            'style': 'max-width: 250px;'
        }),
        help_text='Ingrese solo los números del RUT, sin puntos ni guión'
    )

    def clean_rut_tutor(self):
        rut_tutor = self.cleaned_data['rut_tutor']
        
        # Validar que sea solo números
        if not re.match(r'^\d{7,8}$', rut_tutor):
            raise forms.ValidationError('El RUT debe contener solo números y tener entre 7 y 8 dígitos')
        
        return rut_tutor


class RegistrarMascotaForm(forms.Form):
    """
    Formulario para registrar una nueva mascota.
    """
    
    # Datos básicos de la mascota
    nombre = forms.CharField(
        max_length=100,
        label='Nombre *',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de la mascota'
        })
    )
    
    especie = forms.ModelChoiceField(
        queryset=Especie.objects.filter(activo=True),
        label='Especie *',
        empty_label='Seleccione una especie',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_especie'
        })
    )
    
    raza = forms.ModelChoiceField(
        queryset=Raza.objects.none(),  # Se carga dinámicamente
        label='Raza *',
        empty_label='Primero seleccione una especie',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_raza'
        })
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
        label='Número de Chip *',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de chip de identificación'
        })
    )
    
    SEXO_CHOICES = [
        ('', 'Seleccione un sexo'),
        ('Macho', 'Macho'),
        ('Hembra', 'Hembra'),
    ]
    
    sexo = forms.ChoiceField(
        choices=SEXO_CHOICES,
        label='Sexo *',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    fecha_nacimiento = forms.DateField(
        label='Fecha de Nacimiento',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
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
        })
    )

    def __init__(self, *args, **kwargs):
        self.tutor_id = kwargs.pop('tutor_id', None)
        super().__init__(*args, **kwargs)
        
        # Si se pasa un id de especie, cargar las razas correspondientes
        if 'especie' in self.data:
            try:
                especie_id = int(self.data.get('especie'))
                self.fields['raza'].queryset = Raza.objects.filter(
                    id_especie=especie_id, activo=True
                ).order_by('nombre')
                self.fields['raza'].empty_label = 'Seleccione una raza'
            except (ValueError, TypeError):
                pass

    def clean_nro_chip(self):
        nro_chip = self.cleaned_data['nro_chip']
        
        # Validar que el número de chip no esté repetido
        if Mascota.objects.filter(nro_chip=nro_chip).exists():
            raise forms.ValidationError('Este número de chip ya está registrado en el sistema')
        
        return nro_chip

    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        
        if fecha_nacimiento and fecha_nacimiento > date.today():
            raise forms.ValidationError('La fecha de nacimiento no puede ser futura')
        
        return fecha_nacimiento

    def clean(self):
        cleaned_data = super().clean()
        
        # Validar que se haya seleccionado un tutor
        if not self.tutor_id:
            raise forms.ValidationError('Debe buscar y seleccionar un tutor válido antes de registrar la mascota')
        
        return cleaned_data