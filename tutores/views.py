from django.shortcuts import render, redirect
from core.models import Tutor, Mascota
from .forms import BuscarTutorForm


def buscar_tutor_view(request):
    tutor = None
    mascotas = []
    mensaje = None
    
    if request.method == 'POST':
        form = BuscarTutorForm(request.POST)
        if form.is_valid():
            nro_documento = form.cleaned_data['nro_documento']
            try:
                tutor = Tutor.objects.get(nro_documento=nro_documento)
                mascotas = Mascota.objects.filter(id_tutor=tutor)
            except Tutor.DoesNotExist:
                mensaje = "Tutor no registrado en el sistema"
        else:
            # Si el formulario no es válido, mostrar errores
            pass
    else:
        form = BuscarTutorForm()
    
    return render(request, 'tutores/buscar_tutor.html', {
        'form': form,
        'tutor': tutor,
        'mascotas': mascotas,
        'mensaje': mensaje,
    })
