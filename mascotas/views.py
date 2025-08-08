"""
Vistas para la gestión de mascotas.

Este módulo contiene las vistas para la gestión de mascotas,
incluyendo registro de nuevas mascotas y búsqueda de tutores.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from core.models import Tutor, Mascota, Especie, Raza
from .forms import BuscarTutorMascotaForm, RegistrarMascotaForm
import json
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)


def registrar_mascota_view(request):
    """
    Vista para registrar una nueva mascota.
    Incluye búsqueda de tutor por RUT y formulario de registro.
    """
    tutor_encontrado = None
    mascota_guardada = None
    mensaje_exito = None
    
    # Formularios
    buscar_tutor_form = BuscarTutorMascotaForm()
    registrar_mascota_form = RegistrarMascotaForm()
    
    logger.info(f"Método de request: {request.method}")
    
    if request.method == 'POST':
        logger.info("Procesando POST request")
        logger.info(f"Datos POST: {request.POST}")
        
        # Determinar qué formulario se está enviando
        if 'buscar_tutor' in request.POST:
            # Búsqueda de tutor
            buscar_tutor_form = BuscarTutorMascotaForm(request.POST)
            
            if buscar_tutor_form.is_valid():
                rut_tutor = buscar_tutor_form.cleaned_data['rut_tutor']
                logger.info(f"Buscando tutor con RUT: {rut_tutor}")
                
                # Buscar tutor por RUT (comparando solo los números, sin DV)
                try:
                    tutores = Tutor.objects.all()
                    for tutor in tutores:
                        # Extraer solo números del RUT almacenado
                        rut_sin_dv = re.sub(r'[^\d]', '', tutor.nro_documento)[:-1]  # Quitar último dígito (DV)
                        if rut_sin_dv == rut_tutor:
                            tutor_encontrado = tutor
                            logger.info(f"Tutor encontrado: {tutor_encontrado}")
                            break
                    
                    if not tutor_encontrado:
                        buscar_tutor_form.add_error('rut_tutor', 'No se encontró un tutor con este RUT')
                        logger.info("Tutor no encontrado")
                
                except Exception as e:
                    logger.error(f"Error al buscar tutor: {e}")
                    buscar_tutor_form.add_error('rut_tutor', 'Error al buscar el tutor')
            
        elif 'registrar_mascota' in request.POST:
            # Registro de mascota
            tutor_id = request.POST.get('tutor_id')
            logger.info(f"Registrando mascota para tutor ID: {tutor_id}")
            
            if tutor_id:
                try:
                    tutor_encontrado = Tutor.objects.get(id_tutor=tutor_id)
                    registrar_mascota_form = RegistrarMascotaForm(request.POST, request.FILES, tutor_id=tutor_id)
                    
                    # Configurar queryset de razas si se seleccionó especie
                    if 'especie' in request.POST and request.POST['especie']:
                        especie_id = request.POST['especie']
                        registrar_mascota_form.fields['raza'].queryset = Raza.objects.filter(
                            id_especie=especie_id, activo=True
                        ).order_by('nombre')
                    
                    if registrar_mascota_form.is_valid():
                        logger.info("Formulario de mascota válido, procediendo a crear")
                        logger.info(f"Datos limpios: {registrar_mascota_form.cleaned_data}")
                        
                        try:
                            # Crear la mascota
                            mascota = Mascota.objects.create(
                                id_tutor=tutor_encontrado,
                                id_especie=registrar_mascota_form.cleaned_data['especie'],
                                id_raza=registrar_mascota_form.cleaned_data['raza'],
                                nombre=registrar_mascota_form.cleaned_data['nombre'],
                                nro_chip=registrar_mascota_form.cleaned_data['nro_chip'],
                                sexo=registrar_mascota_form.cleaned_data['sexo'],
                                color=registrar_mascota_form.cleaned_data['color'] or '',
                                fecha_nacimiento=registrar_mascota_form.cleaned_data['fecha_nacimiento'],
                                estado_reproductivo=registrar_mascota_form.cleaned_data['estado_reproductivo'] or '',
                                notas_adicionales=registrar_mascota_form.cleaned_data['notas_adicionales'] or '',
                                estado_vital='Vivo',  # Por defecto
                                consentimiento=bool(registrar_mascota_form.cleaned_data['documento_consentimiento']),
                                fecha_consentimiento=datetime.now().date() if registrar_mascota_form.cleaned_data['documento_consentimiento'] else None,
                                url_doc_consentimiento='',  # Por ahora vacío
                                foto='',  # Por ahora vacío
                                fecha_registro=datetime.now()
                            )
                            
                            logger.info(f"Mascota creada exitosamente: {mascota}")
                            mascota_guardada = mascota
                            mensaje_exito = f"La mascota '{mascota.nombre}' ha sido registrada exitosamente"
                            
                            # Limpiar formularios para nuevo registro
                            buscar_tutor_form = BuscarTutorMascotaForm()
                            registrar_mascota_form = RegistrarMascotaForm()
                            tutor_encontrado = None
                            
                        except Exception as e:
                            logger.error(f"Error al crear mascota: {e}")
                            registrar_mascota_form.add_error(None, f"Error al guardar la mascota: {str(e)}")
                    
                    else:
                        logger.info("Formulario de mascota no válido")
                        logger.info(f"Errores del formulario: {registrar_mascota_form.errors}")
                
                except Tutor.DoesNotExist:
                    logger.error(f"Tutor con ID {tutor_id} no encontrado")
                    registrar_mascota_form.add_error(None, "Tutor no válido. Por favor, busque nuevamente.")
    
    logger.info(f"Tutor encontrado: {tutor_encontrado}")
    logger.info(f"Mascota guardada: {mascota_guardada}")
    
    return render(request, 'mascotas/registrar_mascota.html', {
        'buscar_tutor_form': buscar_tutor_form,
        'registrar_mascota_form': registrar_mascota_form,
        'tutor_encontrado': tutor_encontrado,
        'mascota_guardada': mascota_guardada,
        'mensaje_exito': mensaje_exito,
    })


@csrf_exempt
def cargar_razas(request):
    """
    Vista AJAX para cargar razas según la especie seleccionada.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            especie_id = data.get('especie_id')
            
            if especie_id:
                razas = Raza.objects.filter(
                    id_especie=especie_id, 
                    activo=True
                ).order_by('nombre').values('id_raza', 'nombre')
                
                razas_list = list(razas)
                logger.info(f"Cargando {len(razas_list)} razas para especie {especie_id}")
                
                return JsonResponse({
                    'success': True,
                    'razas': razas_list
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'No se proporcionó ID de especie'
                })
        
        except Exception as e:
            logger.error(f"Error al cargar razas: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    })