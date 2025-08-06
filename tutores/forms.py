from django import forms
from .models import Tutor, Mascota

class BuscarTutorForm(forms.Form):
    rut = forms.CharField(label='RUT del tutor', max_length=10)

class TutorForm(forms.ModelForm):
    class Meta:
        model = Tutor
        fields = '__all__'

class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        exclude = ['tutor']
