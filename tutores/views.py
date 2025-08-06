from django.shortcuts import render, get_object_or_404, redirect
from .models import Tutor
from .forms import BuscarTutorForm, TutorForm, MascotaForm

def buscar_tutor(request):
    tutor = None
    mascotas = None
    if request.method == 'POST':
        form = BuscarTutorForm(request.POST)
        if form.is_valid():
            rut = form.cleaned_data['rut']
            try:
                tutor = Tutor.objects.get(rut=rut)
                mascotas = tutor.mascotas.all()
            except Tutor.DoesNotExist:
                tutor = None
    else:
        form = BuscarTutorForm()

    context = {
        'form': form,
        'tutor': tutor,
        'mascotas': mascotas
    }
    return render(request, 'tutores/buscar_tutor.html', context)
