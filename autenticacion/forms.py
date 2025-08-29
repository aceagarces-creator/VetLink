from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import requests
from django.conf import settings

class VetLinkLoginForm(forms.Form):
    """
    Formulario de login personalizado para VetLink
    """
    username = forms.EmailField(
        label='Usuario',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'id': 'id_username',
            'placeholder': 'Ingrese su correo electrónico',
            'autocomplete': 'email'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'id_password',
            'placeholder': 'Ingrese su contraseña',
            'autocomplete': 'current-password'
        })
    )
    recaptcha_response = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar mensajes de error personalizados
        self.fields['username'].error_messages = {
            'required': 'El correo electrónico es obligatorio.',
            'invalid': 'Ingrese un correo electrónico válido.'
        }
        self.fields['password'].error_messages = {
            'required': 'La contraseña es obligatoria.'
        }

    def clean(self):
        """
        Validación personalizada del formulario
        """
        print("=== DEBUG FORM: Iniciando clean() ===")
        cleaned_data = super().clean()
        print(f"=== DEBUG FORM: cleaned_data después de super(): {cleaned_data} ===")
        
        # Validar reCAPTCHA
        recaptcha_response = cleaned_data.get('recaptcha_response')
        print(f"=== DEBUG FORM: recaptcha_response: {recaptcha_response[:50] if recaptcha_response else 'None'}... ===")
        
        # En desarrollo, permitir continuar sin validación estricta
        if getattr(settings, 'DEBUG', True):
            print("=== DEBUG FORM: DEBUG=True, saltando validación reCAPTCHA ===")
            return cleaned_data
        
        if not recaptcha_response:
            print("=== DEBUG FORM: reCAPTCHA vacío, lanzando error ===")
            raise ValidationError('Por favor complete el reCAPTCHA.')
        
        print("=== DEBUG FORM: reCAPTCHA válido ===")
        return cleaned_data

    def clean_recaptcha_response(self):
        """
        Validar reCAPTCHA (método individual)
        """
        print("=== DEBUG FORM: clean_recaptcha_response() llamado ===")
        recaptcha_response = self.cleaned_data.get('recaptcha_response')
        print(f"=== DEBUG FORM: recaptcha_response en clean_recaptcha_response: {recaptcha_response[:50] if recaptcha_response else 'None'}... ===")
        
        # En desarrollo, permitir continuar sin validación estricta
        if getattr(settings, 'DEBUG', True):
            print("=== DEBUG FORM: DEBUG=True, retornando recaptcha_response ===")
            return recaptcha_response
        
        if not recaptcha_response:
            print("=== DEBUG FORM: reCAPTCHA vacío, lanzando error ===")
            raise ValidationError('Por favor complete el reCAPTCHA.')
        
        # Verificar reCAPTCHA con Google
        data = {
            'secret': getattr(settings, 'RECAPTCHA_SECRET_KEY', ''),
            'response': recaptcha_response
        }
        
        try:
            response = requests.post(
                'https://www.google.com/recaptcha/api/siteverify',
                data=data,
                timeout=5
            )
            result = response.json()
            
            if not result.get('success', False):
                print("=== DEBUG FORM: reCAPTCHA falló en Google ===")
                raise ValidationError('Verificación reCAPTCHA fallida. Por favor intente nuevamente.')
                
        except requests.RequestException:
            print("=== DEBUG FORM: Error en request a Google reCAPTCHA ===")
            raise ValidationError('Error al verificar reCAPTCHA. Por favor intente nuevamente.')
        
        print("=== DEBUG FORM: reCAPTCHA válido ===")
        return recaptcha_response


