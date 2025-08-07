from django import forms
import re

class BuscarTutorForm(forms.Form):
    nro_documento = forms.CharField(
        label='Ingrese el Rut del tutor(*)',
        max_length=12,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: 12345678-9',
            'class': 'form-control',
            'autocomplete': 'off',
            'style': 'border-radius: 5px; border: 1px solid #ddd; padding: 8px 12px; font-size: 14px;'
        })
    )
    
    def clean_nro_documento(self):
        rut = self.cleaned_data['nro_documento']
        
        # Limpiar espacios y convertir a mayúsculas
        rut = rut.strip().upper()
        
        # Validar formato básico
        if not re.match(r'^\d{7,8}-[\dK]$', rut):
            raise forms.ValidationError(
                'El RUT debe tener el formato: 12345678-9 (con dígito verificador)'
            )
        
        # Validar dígito verificador
        if not self.validar_digito_verificador(rut):
            raise forms.ValidationError(
                'El dígito verificador del RUT no es válido'
            )
        
        return rut
    
    def validar_digito_verificador(self, rut):
        """
        Valida el dígito verificador de un RUT chileno.
        """
        try:
            # Separar número y dígito verificador
            numero, dv = rut.split('-')
            
            # Calcular dígito verificador
            suma = 0
            multiplicador = 2
            
            for digito in reversed(numero):
                suma += int(digito) * multiplicador
                multiplicador = multiplicador + 1 if multiplicador < 7 else 2
            
            resto = suma % 11
            dv_calculado = 11 - resto
            
            # Ajustar casos especiales
            if dv_calculado == 11:
                dv_calculado = '0'
            elif dv_calculado == 10:
                dv_calculado = 'K'
            else:
                dv_calculado = str(dv_calculado)
            
            return dv == dv_calculado
            
        except (ValueError, IndexError):
            return False