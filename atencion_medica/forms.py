"""
Formularios para el módulo de atención médica.
"""

from django import forms
from core.models import Mascota, PersonalClinica, ServicioDetalle, ClinicaVeterinaria
from .models import AtencionMedica, DocumentoAtencion


class BuscarMascotaAtencionForm(forms.Form):
    """
    Formulario para buscar una mascota por número de chip para registrar atención médica.
    """
    nro_chip = forms.CharField(
        label='Número de Chip',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el número de chip de la mascota',
            'style': 'font-size: 0.8rem; padding: 8px 12px; border-radius: 4px; border: 1px solid #ddd;'
        }),
        help_text='Ingrese el número de chip de la mascota para registrar una atención médica'
    )


class AtencionMedicaForm(forms.ModelForm):
    """
    Formulario para registrar una nueva atención médica.
    """
    class Meta:
        model = AtencionMedica
        fields = [
            'id_mascota', 'id_clinica', 'id_personal', 'id_servicio_detalle',
            'fecha_atencion', 'peso', 'temperatura', 'motivo_atencion',
            'detalle_clinico', 'diagnostico', 'tratamiento'
        ]
        widgets = {
            'id_mascota': forms.Select(attrs={
                'class': 'form-control',
                'style': 'font-size: 0.8rem; padding: 8px 12px; border-radius: 4px; border: 1px solid #ddd;'
            }),
            'id_clinica': forms.Select(attrs={
                'class': 'form-control',
                'style': 'font-size: 0.8rem; padding: 8px 12px; border-radius: 4px; border: 1px solid #ddd;'
            }),
            'id_personal': forms.Select(attrs={
                'class': 'form-control',
                'style': 'font-size: 0.8rem; padding: 8px 12px; border-radius: 4px; border: 1px solid #ddd;'
            }),
            'id_servicio_detalle': forms.Select(attrs={
                'class': 'form-control',
                'style': 'font-size: 0.8rem; padding: 8px 12px; border-radius: 4px; border: 1px solid #ddd;'
            }),
            'fecha_atencion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'style': 'font-size: 0.8rem; padding: 8px 12px; border-radius: 4px; border: 1px solid #ddd;'
            }),
            'peso': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0',
                'placeholder': 'Ej: 5.5',
                'style': 'font-size: 0.8rem; padding: 8px 12px; border-radius: 4px; border: 1px solid #ddd;'
            }),
            'temperatura': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0',
                'placeholder': 'Ej: 38.5',
                'style': 'font-size: 0.8rem; padding: 8px 12px; border-radius: 4px; border: 1px solid #ddd;'
            }),
            'motivo_atencion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describa el motivo de la atención',
                'style': 'font-size: 0.8rem; padding: 8px 12px; border-radius: 4px; border: 1px solid #ddd; resize: vertical;'
            }),
            'detalle_clinico': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Detalle clínico de la atención',
                'style': 'font-size: 0.8rem; padding: 8px 12px; border-radius: 4px; border: 1px solid #ddd; resize: vertical;'
            }),
            'diagnostico': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Diagnóstico de la atención',
                'style': 'font-size: 0.8rem; padding: 8px 12px; border-radius: 4px; border: 1px solid #ddd; resize: vertical;'
            }),
            'tratamiento': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tratamiento prescrito',
                'style': 'font-size: 0.8rem; padding: 8px 12px; border-radius: 4px; border: 1px solid #ddd; resize: vertical;'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar querysets iniciales
        self.fields['id_clinica'].queryset = ClinicaVeterinaria.objects.all().order_by('nombre')
        self.fields['id_personal'].queryset = PersonalClinica.objects.all().order_by('nombres')
        self.fields['id_servicio_detalle'].queryset = ServicioDetalle.objects.filter(activo=True).order_by('nombre')


class DocumentoAtencionForm(forms.ModelForm):
    """
    Formulario para adjuntar documentos a una atención médica.
    """
    class Meta:
        model = DocumentoAtencion
        fields = ['tipo_documento', 'archivo']
        widgets = {
            'tipo_documento': forms.Select(attrs={
                'class': 'form-control',
                'style': 'font-size: 0.8rem; padding: 8px 12px; border-radius: 4px; border: 1px solid #ddd;'
            }),
            'archivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png',
                'style': 'font-size: 0.8rem; padding: 8px 12px; border-radius: 4px; border: 1px solid #ddd;'
            }),
        }
