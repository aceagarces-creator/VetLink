"""
Vistas para el módulo de atención médica.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
import json
import logging
import os
import uuid
from datetime import datetime

from core.models import Mascota, PersonalClinica, ServicioDetalle, ClinicaVeterinaria, Servicio
from core.clinicaVeterinaria_models import ClinicaServicio
from .models import AtencionMedica, DocumentoAtencion
from .forms import BuscarMascotaAtencionForm, AtencionMedicaForm, DocumentoAtencionForm

logger = logging.getLogger(__name__)


def registrar_atencion_unificada_view(request):
    """
    Vista unificada para registrar atención médica en un solo formulario.
    Combina la búsqueda de mascota y el registro de atención médica.
    """
    mascota_encontrada = None
    atencion_guardada = None
    mensaje_exito = None
    mensaje_error = None
    
    # Formularios
    buscar_form = BuscarMascotaAtencionForm()
    atencion_form = AtencionMedicaForm()
    
    if request.method == 'POST':
        # Determinar qué formulario se está enviando
        if 'buscar_mascota' in request.POST:
            # Búsqueda de mascota
            buscar_form = BuscarMascotaAtencionForm(request.POST)
            
            if buscar_form.is_valid():
                nro_chip = buscar_form.cleaned_data['nro_chip']
                logger.info(f"Buscando mascota con chip para atención médica: {nro_chip}")
                
                try:
                    # Buscar mascota por número de chip
                    mascota_encontrada = Mascota.objects.select_related(
                        'id_tutor',
                        'id_especie',
                        'id_raza'
                    ).get(nro_chip=nro_chip)
                    
                    logger.info(f"Mascota encontrada para atención: {mascota_encontrada}")
                    
                    # Configurar el formulario de atención médica con la mascota encontrada
                    atencion_form = AtencionMedicaForm(initial={
                        'id_mascota': mascota_encontrada,
                        'fecha_atencion': timezone.now().date(),
                    })
                    
                except Mascota.DoesNotExist:
                    mensaje_error = f"No se encontró una mascota con el número de chip: {nro_chip}"
                    logger.info(f"Mascota no encontrada con chip: {nro_chip}")
        
        elif 'registrar_atencion' in request.POST:
            # Registro de atención médica
            nro_chip = request.POST.get('nro_chip_busqueda')
            
            if nro_chip:
                try:
                    mascota_encontrada = Mascota.objects.select_related(
                        'id_tutor',
                        'id_especie',
                        'id_raza'
                    ).get(nro_chip=nro_chip)
                    
                    atencion_form = AtencionMedicaForm(request.POST, request.FILES)
                    
                    if atencion_form.is_valid():
                        try:
                            with transaction.atomic():
                                # Crear la atención médica
                                atencion = atencion_form.save(commit=False)
                                atencion.id_mascota = mascota_encontrada
                                atencion.estado = 'PENDIENTE'
                                atencion.save()
                                
                                # Procesar documentos adjuntos
                                documentos_guardados = []
                                for i in range(1, 4):  # Máximo 3 documentos
                                    tipo_doc_key = f'tipo_documento_{i}'
                                    archivo_key = f'archivo_{i}'
                                    
                                    if tipo_doc_key in request.POST and archivo_key in request.FILES:
                                        tipo_documento = request.POST[tipo_doc_key]
                                        archivo = request.FILES[archivo_key]
                                        
                                        # Validar tipo de archivo
                                        extensiones_permitidas = ['.pdf', '.jpg', '.jpeg', '.png']
                                        nombre_archivo = archivo.name.lower()
                                        if any(nombre_archivo.endswith(ext) for ext in extensiones_permitidas):
                                            # Generar nombre único para el archivo
                                            extension = archivo.name.split('.')[-1].lower()
                                            fecha = datetime.now().strftime('%Y%m%d')
                                            uuid_short = str(uuid.uuid4())[:8]
                                            nuevo_nombre = f"doc_{atencion.id_atencion}_{fecha}_{uuid_short}.{extension}"
                                            
                                            # Crear documento
                                            documento = DocumentoAtencion.objects.create(
                                                id_atencion=atencion,
                                                tipo_documento=tipo_documento,
                                                nombre_archivo=archivo.name,
                                                archivo=archivo
                                            )
                                            
                                            # Renombrar archivo
                                            ruta_original = documento.archivo.path
                                            directorio = os.path.dirname(ruta_original)
                                            nueva_ruta = os.path.join(directorio, nuevo_nombre)
                                            
                                            if os.path.exists(ruta_original):
                                                os.rename(ruta_original, nueva_ruta)
                                                documento.archivo.name = f'documentos_atencion/{nuevo_nombre}'
                                                documento.save()
                                            
                                            documentos_guardados.append(documento)
                                            logger.info(f"Documento guardado: {documento}")
                                
                                atencion_guardada = atencion
                                mensaje_exito = f"Atención médica registrada exitosamente para {mascota_encontrada.nombre}"
                                logger.info(f"Atención médica creada: {atencion.id_atencion}")
                                
                                # Limpiar formularios para nuevo registro
                                buscar_form = BuscarMascotaAtencionForm()
                                atencion_form = AtencionMedicaForm()
                                mascota_encontrada = None
                                
                        except Exception as e:
                            logger.error(f"Error al registrar atención médica: {e}")
                            mensaje_error = f"Error al registrar la atención médica: {str(e)}"
                    else:
                        logger.info("Formulario de atención médica no válido")
                        logger.info(f"Errores del formulario: {atencion_form.errors}")
                        
                except Mascota.DoesNotExist:
                    mensaje_error = f"No se encontró una mascota con el número de chip: {nro_chip}"
    
    # Obtener el médico tratante con usuario = 1
    medico_tratante = None
    try:
        medico_tratante = PersonalClinica.objects.get(usuario=1)
        logger.info(f"Médico tratante obtenido: {medico_tratante}")
    except PersonalClinica.DoesNotExist:
        logger.warning("No se encontró médico tratante con usuario = 1")
    
    # Obtener servicios y servicios detalle asociados a la clínica del usuario autenticado
    # Hipotéticamente estamos con id_usuario = 1 e id_clinica = 1
    try:
        # Obtener la clínica del usuario autenticado
        usuario_autenticado = PersonalClinica.objects.get(usuario=1)
        clinica_id = usuario_autenticado.id_clinica.id_clinica
        logger.info(f"Clínica del usuario autenticado: {clinica_id}")
    except PersonalClinica.DoesNotExist:
        # Fallback a clínica 1 si no se encuentra el usuario
        clinica_id = 1
        logger.warning("Usuario no encontrado, usando clínica 1 como fallback")
    
    # Obtener servicios detalle asociados a la clínica
    clinica_servicios = ClinicaServicio.objects.filter(
        id_clinica=clinica_id,
        activo=True
    ).select_related('id_servicio_detalle', 'id_servicio_detalle__id_servicio')
    
    # Extraer servicios únicos y servicios detalle
    servicios = []
    servicios_detalle = []
    servicios_ids = set()
    
    for cs in clinica_servicios:
        servicio = cs.id_servicio_detalle.id_servicio
        if servicio.id_servicio not in servicios_ids:
            servicios.append(servicio)
            servicios_ids.add(servicio.id_servicio)
        servicios_detalle.append(cs.id_servicio_detalle)
    
    return render(request, 'atencion_medica/registrar_atencion.html', {
        'buscar_form': buscar_form,
        'atencion_form': atencion_form,
        'mascota_encontrada': mascota_encontrada,
        'atencion_guardada': atencion_guardada,
        'mensaje_exito': mensaje_exito,
        'mensaje_error': mensaje_error,
        'medico_tratante': medico_tratante,
        'servicios': servicios,
        'servicios_detalle': servicios_detalle,
    })


def buscar_mascota_atencion_view(request):
    """
    Vista para buscar una mascota por número de chip para registrar atención médica.
    """
    mascota_encontrada = None
    mensaje = None
    
    if request.method == 'POST':
        form = BuscarMascotaAtencionForm(request.POST)
        
        if form.is_valid():
            nro_chip = form.cleaned_data['nro_chip']
            logger.info(f"Buscando mascota con chip para atención médica: {nro_chip}")
            
            try:
                # Buscar mascota por número de chip
                mascota_encontrada = Mascota.objects.select_related(
                    'id_tutor',
                    'id_especie',
                    'id_raza'
                ).get(nro_chip=nro_chip)
                
                logger.info(f"Mascota encontrada para atención: {mascota_encontrada}")
                
                # Redirigir al formulario de atención médica
                return redirect('atencion_medica:registrar_atencion', mascota_id=mascota_encontrada.id_mascota)
                
            except Mascota.DoesNotExist:
                mensaje = f"No se encontró una mascota con el número de chip: {nro_chip}"
                logger.info(f"Mascota no encontrada con chip: {nro_chip}")
    else:
        form = BuscarMascotaAtencionForm()
    
    return render(request, 'atencion_medica/buscar_mascota_atencion.html', {
        'form': form,
        'mascota_encontrada': mascota_encontrada,
        'mensaje': mensaje,
    })


def registrar_atencion_view(request, mascota_id):
    """
    Vista para registrar una nueva atención médica para una mascota específica.
    """
    mascota = get_object_or_404(Mascota, id_mascota=mascota_id)
    atencion_guardada = None
    mensaje_exito = None
    
    if request.method == 'POST':
        form = AtencionMedicaForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Crear la atención médica
                    atencion = form.save(commit=False)
                    atencion.id_mascota = mascota
                    atencion.estado = 'PENDIENTE'
                    atencion.save()
                    
                    # Procesar documentos adjuntos
                    documentos_guardados = []
                    for i in range(1, 4):  # Máximo 3 documentos
                        tipo_doc_key = f'tipo_documento_{i}'
                        archivo_key = f'archivo_{i}'
                        
                        if tipo_doc_key in request.POST and archivo_key in request.FILES:
                            tipo_documento = request.POST[tipo_doc_key]
                            archivo = request.FILES[archivo_key]
                            
                            # Validar tipo de archivo
                            extensiones_permitidas = ['.pdf', '.jpg', '.jpeg', '.png']
                            nombre_archivo = archivo.name.lower()
                            if any(nombre_archivo.endswith(ext) for ext in extensiones_permitidas):
                                # Generar nombre único para el archivo
                                extension = archivo.name.split('.')[-1].lower()
                                fecha = datetime.now().strftime('%Y%m%d')
                                uuid_short = str(uuid.uuid4())[:8]
                                nuevo_nombre = f"doc_{atencion.id_atencion}_{fecha}_{uuid_short}.{extension}"
                                
                                # Crear documento
                                documento = DocumentoAtencion.objects.create(
                                    id_atencion=atencion,
                                    tipo_documento=tipo_documento,
                                    nombre_archivo=archivo.name,
                                    archivo=archivo
                                )
                                
                                # Renombrar archivo
                                ruta_original = documento.archivo.path
                                directorio = os.path.dirname(ruta_original)
                                nueva_ruta = os.path.join(directorio, nuevo_nombre)
                                
                                if os.path.exists(ruta_original):
                                    os.rename(ruta_original, nueva_ruta)
                                    documento.archivo.name = f'documentos_atencion/{nuevo_nombre}'
                                    documento.save()
                                
                                documentos_guardados.append(documento)
                                logger.info(f"Documento guardado: {documento}")
                    
                    atencion_guardada = atencion
                    mensaje_exito = f"Atención médica registrada exitosamente para {mascota.nombre}"
                    logger.info(f"Atención médica creada: {atencion.id_atencion}")
                    
            except Exception as e:
                logger.error(f"Error al registrar atención médica: {e}")
                messages.error(request, f"Error al registrar la atención médica: {str(e)}")
    else:
        form = AtencionMedicaForm(initial={
            'id_mascota': mascota,
            'fecha_atencion': timezone.now().date(),
        })
    
    return render(request, 'atencion_medica/registrar_atencion.html', {
        'form': form,
        'mascota': mascota,
        'atencion_guardada': atencion_guardada,
        'mensaje_exito': mensaje_exito,
    })


@csrf_exempt
def cargar_servicios_detalle(request):
    """
    Vista AJAX para cargar servicios detalle según el servicio seleccionado.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            servicio_id = data.get('servicio_id')
            
            if servicio_id:
                servicios_detalle = ServicioDetalle.objects.filter(
                    id_servicio=servicio_id, 
                    activo=True
                ).order_by('nombre').values('id_servicio_detalle', 'nombre')
                
                servicios_list = list(servicios_detalle)
                logger.info(f"Cargando {len(servicios_list)} servicios detalle para servicio {servicio_id}")
                
                return JsonResponse({
                    'success': True,
                    'servicios_detalle': servicios_list
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'No se proporcionó ID de servicio'
                })
        
        except Exception as e:
            logger.error(f"Error al cargar servicios detalle: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    })


def listar_atenciones_view(request):
    """
    Vista para listar todas las atenciones médicas registradas.
    """
    atenciones = AtencionMedica.objects.select_related(
        'id_mascota',
        'id_mascota__id_tutor',
        'id_clinica',
        'id_personal',
        'id_servicio_detalle',
        'id_servicio_detalle__id_servicio'
    ).order_by('-fecha_atencion', '-fecha_registro')
    
    return render(request, 'atencion_medica/listar_atenciones.html', {
        'atenciones': atenciones,
    })


def detalle_atencion_view(request, atencion_id):
    """
    Vista para mostrar el detalle de una atención médica específica.
    """
    atencion = get_object_or_404(AtencionMedica, id_atencion=atencion_id)
    
    return render(request, 'atencion_medica/detalle_atencion.html', {
        'atencion': atencion,
    })
