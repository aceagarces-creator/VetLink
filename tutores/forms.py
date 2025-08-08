from django import forms
import re
from datetime import date
from core.models import Tutor, Region, Provincia, Comuna

class BuscarTutorForm(forms.Form):
    nro_documento = forms.CharField(
        label='Ingrese el Rut del tutor(*)',
        max_length=12,
        error_messages={
            'required': 'El RUT es obligatorio',
            'max_length': 'El RUT no puede tener más de 12 caracteres',
        },
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: 15468064-0',
            'class': 'form-control',
            'style': 'border-radius: 5px; border: 1px solid #ddd; padding: 10px 12px; font-size: 0.65rem; max-width: 250px;',
            'pattern': '[0-9Kk-]*',
            'oninput': 'this.value = this.value.replace(/[^0-9Kk-]/g, "").replace(/k/g, "K");'
        })
    )

    def clean_nro_documento(self):
        nro_documento = self.cleaned_data['nro_documento']
        
        # Limpiar el RUT: solo permitir números, guión y K
        rut_limpio = ''.join(c for c in nro_documento if c.isdigit() or c == '-' or c.upper() == 'K')
        
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
        
        # Calcular dígito verificador
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

class RegistrarTutorForm(forms.Form):
    nro_documento = forms.CharField(
        label='Rut (*)',
        max_length=12,
        error_messages={
            'required': 'El RUT es obligatorio',
            'max_length': 'El RUT no puede tener más de 12 caracteres',
        },
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: 15468064-0',
            'class': 'form-control',
            'style': 'border-radius: 5px; border: 1px solid #ddd; padding: 10px 12px; font-size: 0.65rem;',
            'pattern': '[0-9Kk-]*',
            'oninput': 'this.value = this.value.replace(/[^0-9Kk-]/g, "").replace(/k/g, "K");'
        })
    )
    
    nombres = forms.CharField(
        label='Nombres (*)',
        max_length=100,
        error_messages={
            'required': 'Los nombres son obligatorios',
            'max_length': 'Los nombres no pueden tener más de 100 caracteres',
        },
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese nombres',
            'class': 'form-control',
            'style': 'border-radius: 5px; border: 1px solid #ddd; padding: 10px 12px; font-size: 0.65rem;'
        })
    )
    
    apellido_paterno = forms.CharField(
        label='Apellido Paterno (*)',
        max_length=100,
        error_messages={
            'required': 'El apellido paterno es obligatorio',
            'max_length': 'El apellido paterno no puede tener más de 100 caracteres',
        },
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese apellido paterno',
            'class': 'form-control',
            'style': 'border-radius: 5px; border: 1px solid #ddd; padding: 10px 12px; font-size: 0.65rem;'
        })
    )
    
    apellido_materno = forms.CharField(
        label='Apellido Materno',
        max_length=100,
        required=False,
        error_messages={
            'max_length': 'El apellido materno no puede tener más de 100 caracteres',
        },
        widget=forms.TextInput(attrs={
            'placeholder': 'Opcional',
            'class': 'form-control',
            'style': 'border-radius: 5px; border: 1px solid #ddd; padding: 10px 12px; font-size: 0.65rem;'
        })
    )
    
    email = forms.EmailField(
        label='Correo electrónico (*)',
        error_messages={
            'required': 'El correo electrónico es obligatorio',
            'invalid': 'Ingrese un correo electrónico válido',
        },
        widget=forms.EmailInput(attrs={
            'placeholder': 'ejemplo@correo.com',
            'class': 'form-control',
            'style': 'border-radius: 5px; border: 1px solid #ddd; padding: 10px 12px; font-size: 0.65rem;'
        })
    )
    
    celular = forms.CharField(
        label='Celular (*)',
        max_length=15,
        error_messages={
            'required': 'El celular es obligatorio',
            'max_length': 'El celular no puede tener más de 15 caracteres',
        },
        widget=forms.TextInput(attrs={
            'placeholder': 'Solo números',
            'class': 'form-control',
            'style': 'border-radius: 5px; border: 1px solid #ddd; padding: 10px 12px; font-size: 0.65rem;'
        })
    )
    
    telefono = forms.CharField(
        label='Teléfono',
        max_length=15,
        required=False,
        error_messages={
            'max_length': 'El teléfono no puede tener más de 15 caracteres',
        },
        widget=forms.TextInput(attrs={
            'placeholder': 'Opcional',
            'class': 'form-control',
            'style': 'border-radius: 5px; border: 1px solid #ddd; padding: 10px 12px; font-size: 0.65rem;'
        })
    )
    
    fecha_nacimiento = forms.DateField(
        label='Fecha de Nacimiento (*)',
        error_messages={
            'required': 'La fecha de nacimiento es obligatoria',
            'invalid': 'Ingrese una fecha válida',
        },
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'style': 'border-radius: 5px; border: 1px solid #ddd; padding: 10px 12px; font-size: 0.65rem;'
        })
    )
    
    region = forms.ModelChoiceField(
        label='Región (*)',
        queryset=Region.objects.all(),
        error_messages={
            'required': 'Debe seleccionar una región',
            'invalid_choice': 'Seleccione una región válida',
        },
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'border-radius: 5px; border: 1px solid #ddd; padding: 10px 12px; font-size: 0.65rem;'
        })
    )
    
    provincia = forms.ModelChoiceField(
        label='Provincia (*)',
        queryset=Provincia.objects.none(),
        error_messages={
            'required': 'Debe seleccionar una provincia',
            'invalid_choice': 'Seleccione una provincia válida',
        },
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'border-radius: 5px; border: 1px solid #ddd; padding: 10px 12px; font-size: 0.65rem;'
        })
    )
    
    comuna = forms.ModelChoiceField(
        label='Comuna (*)',
        queryset=Comuna.objects.none(),
        error_messages={
            'required': 'Debe seleccionar una comuna',
            'invalid_choice': 'Seleccione una comuna válida',
        },
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'border-radius: 5px; border: 1px solid #ddd; padding: 10px 12px; font-size: 0.65rem;'
        })
    )
    
    calle = forms.CharField(
        label='Calle (*)',
        max_length=100,
        error_messages={
            'required': 'La calle es obligatoria',
            'max_length': 'La calle no puede tener más de 100 caracteres',
        },
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese nombre de la calle',
            'class': 'form-control',
            'style': 'border-radius: 5px; border: 1px solid #ddd; padding: 10px 12px; font-size: 0.65rem;'
        })
    )
    
    numero = forms.CharField(
        label='Número (*)',
        max_length=10,
        error_messages={
            'required': 'El número es obligatorio',
            'max_length': 'El número no puede tener más de 10 caracteres',
        },
        widget=forms.TextInput(attrs={
            'placeholder': 'Solo números',
            'class': 'form-control',
            'style': 'border-radius: 5px; border: 1px solid #ddd; padding: 10px 12px; font-size: 0.65rem;'
        })
    )
    
    complemento = forms.CharField(
        label='Complemento',
        max_length=100,
        required=False,
        error_messages={
            'max_length': 'El complemento no puede tener más de 100 caracteres',
        },
        widget=forms.TextInput(attrs={
            'placeholder': 'Opcional',
            'class': 'form-control',
            'style': 'border-radius: 5px; border: 1px solid #ddd; padding: 10px 12px; font-size: 0.65rem;'
        })
    )
    
    codigo_postal = forms.CharField(
        label='Código Postal',
        max_length=10,
        required=False,
        error_messages={
            'max_length': 'El código postal no puede tener más de 10 caracteres',
        },
        widget=forms.TextInput(attrs={
            'placeholder': 'Opcional',
            'class': 'form-control',
            'style': 'border-radius: 5px; border: 1px solid #ddd; padding: 10px 12px; font-size: 0.65rem;'
        })
    )

    def __init__(self, *args, **kwargs):
        self.tutor_id = kwargs.pop('tutor_id', None)
        super().__init__(*args, **kwargs)

    def clean_nro_documento(self):
        nro_documento = self.cleaned_data['nro_documento']
        
        # Limpiar el RUT: solo permitir números, guión y K
        rut_limpio = ''.join(c for c in nro_documento if c.isdigit() or c == '-' or c.upper() == 'K')
        
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
        
        # Calcular dígito verificador
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
        
        # Solo validar unicidad si no estamos en modo edición
        if not self.tutor_id:
            if Tutor.objects.filter(nro_documento=rut_limpio).exists():
                raise forms.ValidationError('Este RUT ya está registrado en el sistema')
        
        return rut_limpio

    def clean_celular(self):
        celular = self.cleaned_data['celular']
        if not celular.isdigit():
            raise forms.ValidationError('El celular debe contener solo números')
        return celular

    def clean_numero(self):
        numero = self.cleaned_data['numero']
        if not numero.isdigit():
            raise forms.ValidationError('El número debe contener solo números')
        return numero

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data['fecha_nacimiento']
        if fecha > date.today():
            raise forms.ValidationError('La fecha de nacimiento no puede ser futura')
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        region = cleaned_data.get('region')
        provincia = cleaned_data.get('provincia')
        comuna = cleaned_data.get('comuna')
        
        if region and provincia:
            if provincia.id_region != region:
                raise forms.ValidationError('La provincia seleccionada no pertenece a la región elegida')
        
        if provincia and comuna:
            if comuna.id_provincia != provincia:
                raise forms.ValidationError('La comuna seleccionada no pertenece a la provincia elegida')
        
        return cleaned_data