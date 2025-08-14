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
    logger.info("=== INICIO DE VISTA registrar_atencion_unificada_view ===")
    logger.info(f"Método de request: {request.method}")
    logger.info(f"URL: {request.path}")
    logger.info(f"POST data: {request.POST}")
    logger.info(f"FILES data: {request.FILES}")
    
    mascota_encontrada = None
    atencion_guardada = None
    mensaje_exito = None
    mensaje_error = None
    
    # Formularios
    buscar_form = BuscarMascotaAtencionForm()
    atencion_form = AtencionMedicaForm()
    
    # Obtener médico tratante para mostrar en el formulario
    try:
        medico_tratante = PersonalClinica.objects.get(usuario=1)
        logger.info(f"Médico tratante obtenido: {medico_tratante.nombres} {medico_tratante.apellido_paterno}")
    except PersonalClinica.DoesNotExist:
        medico_tratante = None
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
        # Verificar que el servicio detalle existe y está activo
        if cs.id_servicio_detalle and cs.id_servicio_detalle.activo:
            servicio = cs.id_servicio_detalle.id_servicio
            if servicio.id_servicio not in servicios_ids:
                servicios.append(servicio)
                servicios_ids.add(servicio.id_servicio)
            servicios_detalle.append(cs.id_servicio_detalle)
    
    # Ordenar servicios alfabéticamente
    servicios.sort(key=lambda x: x.nombre)
    
    logger.info(f"Servicios encontrados para clínica {clinica_id}: {[s.nombre for s in servicios]}")
    logger.info(f"Servicios detalle encontrados para clínica {clinica_id}: {[sd.nombre for sd in servicios_detalle]}")
    
    if request.method == 'POST':
        logger.info("=== DETECTADO POST REQUEST ===")
        logger.info(f"Keys en POST: {list(request.POST.keys())}")
        logger.info(f"'registrar_atencion' en POST: {'registrar_atencion' in request.POST}")
        logger.info(f"'buscar_mascota' en POST: {'buscar_mascota' in request.POST}")
        
        # Determinar qué formulario se está enviando
        if 'buscar_mascota' in request.POST:
            logger.info("=== PROCESANDO BÚSQUEDA DE MASCOTA ===")
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
            logger.info("=== PROCESANDO REGISTRO DE ATENCIÓN ===")
            # Registro de atención médica
            logger.info("=== INICIO DE REGISTRO DE ATENCIÓN MÉDICA ===")
            logger.info(f"Datos POST recibidos: {request.POST}")
            logger.info(f"Archivos recibidos: {request.FILES}")
            
            try:
                # Obtener datos del formulario
                nro_chip = request.POST.get('nro_chip_busqueda')
                logger.info(f"Número de chip obtenido: {nro_chip}")
                
                if not nro_chip:
                    mensaje_error = "No se proporcionó el número de chip de la mascota"
                    logger.error("No se encontró número de chip en el formulario")
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
                
                # Buscar mascota
                try:
                    mascota_encontrada = Mascota.objects.select_related(
                        'id_tutor',
                        'id_especie',
                        'id_raza'
                    ).get(nro_chip=nro_chip)
                except Mascota.DoesNotExist:
                    mensaje_error = f"No se encontró una mascota con el número de chip: {nro_chip}"
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
                
                # Obtener clínica del usuario autenticado
                try:
                    usuario_autenticado = PersonalClinica.objects.get(usuario=1)
                    clinica = usuario_autenticado.id_clinica
                except PersonalClinica.DoesNotExist:
                    # Fallback a clínica 1
                    clinica = ClinicaVeterinaria.objects.get(id_clinica=1)
                
                # Obtener médico tratante
                try:
                    medico_tratante = PersonalClinica.objects.get(usuario=1)
                except PersonalClinica.DoesNotExist:
                    mensaje_error = "No se encontró el médico tratante"
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
                
                # Validar documentos adjuntos
                documentos_a_procesar = []
                logger.info(f"Archivos en request.FILES: {list(request.FILES.keys())}")
                logger.info(f"Campos en request.POST: {list(request.POST.keys())}")
                
                for i in range(5):  # Máximo 5 documentos
                    file_key = f'documento_{i}'
                    tipo_key = f'tipo_documento_{i}'
                    nombre_key = f'nombre_documento_{i}'
                    
                    logger.info(f"Verificando documento {i}:")
                    logger.info(f"  - {file_key} en FILES: {file_key in request.FILES}")
                    logger.info(f"  - {tipo_key} en POST: {tipo_key in request.POST}")
                    logger.info(f"  - {nombre_key} en POST: {nombre_key in request.POST}")
                    
                    if file_key in request.FILES and tipo_key in request.POST and nombre_key in request.POST:
                        archivo = request.FILES[file_key]
                        tipo_documento = request.POST[tipo_key]
                        nombre_documento = request.POST[nombre_key]
                        
                        # Validar que todos los campos estén completos
                        if not tipo_documento or not nombre_documento:
                            mensaje_error = "Todos los campos de documentos adjuntos deben estar completos"
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
                        
                        # Validar tipo de archivo
                        extensiones_permitidas = ['.pdf', '.jpg', '.jpeg', '.png']
                        nombre_archivo = archivo.name.lower()
                        if not any(nombre_archivo.endswith(ext) for ext in extensiones_permitidas):
                            mensaje_error = f"Tipo de archivo no permitido para {archivo.name}. Solo se aceptan PDF, JPG, JPEG y PNG"
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
                        
                        # Validar tamaño (máximo 5MB)
                        if archivo.size > 5 * 1024 * 1024:
                            mensaje_error = f"El archivo {archivo.name} es demasiado grande. Máximo 5MB"
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
                        
                        documentos_a_procesar.append({
                            'archivo': archivo,
                            'tipo_documento': tipo_documento,
                            'nombre_documento': nombre_documento
                        })
                
                # Crear atención médica usando el modelo del core
                with transaction.atomic():
                    logger.info("=== INICIANDO TRANSACCIÓN ===")
                    
                    # Crear la atención clínica
                    from core.atencionClinica_models import AtencionClinica, DocumentoAdjunto
                    
                    # Preparar datos para la atención
                    servicio_detalle_id = request.POST.get('id_servicio_detalle')
                    fecha_atencion = request.POST.get('fecha_atencion')
                    peso = request.POST.get('peso')
                    temperatura = request.POST.get('temperatura')
                    motivo = request.POST.get('detalle_atencion')
                    diagnostico = request.POST.get('diagnostico')
                    tratamiento = request.POST.get('tratamiento')
                    
                    logger.info(f"Servicio detalle ID: {servicio_detalle_id}")
                    logger.info(f"Fecha atención: {fecha_atencion}")
                    logger.info(f"Peso: {peso}")
                    logger.info(f"Temperatura: {temperatura}")
                    logger.info(f"Motivo: {motivo}")
                    logger.info(f"Diagnóstico: {diagnostico}")
                    logger.info(f"Tratamiento: {tratamiento}")
                    
                    # Validar que el servicio detalle existe y está activo
                    try:
                        servicio_detalle = ServicioDetalle.objects.get(
                            id_servicio_detalle=servicio_detalle_id,
                            activo=True
                        )
                        logger.info(f"Servicio detalle validado: {servicio_detalle.id_servicio_detalle} - {servicio_detalle.nombre}")
                        logger.info(f"Servicio detalle pertenece al servicio: {servicio_detalle.id_servicio.id_servicio} - {servicio_detalle.id_servicio.nombre}")
                    except ServicioDetalle.DoesNotExist:
                        logger.error(f"Servicio detalle {servicio_detalle_id} no encontrado o no está activo")
                        mensaje_error = f"El servicio detalle seleccionado no es válido"
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
                    
                    # Log de todos los datos antes de crear la atención
                    logger.info("=== DATOS PARA CREAR ATENCIÓN ===")
                    logger.info(f"id_mascota: {mascota_encontrada.id_mascota}")
                    logger.info(f"id_clinica: {clinica.id_clinica}")
                    logger.info(f"id_personal: {medico_tratante.id_personal}")
                    logger.info(f"id_servicio_detalle: {servicio_detalle.id_servicio_detalle}")
                    logger.info(f"fecha_atencion: {fecha_atencion}")
                    logger.info(f"peso_kg: {peso}")
                    logger.info(f"temperatura_c: {temperatura}")
                    
                    # Guardar directamente el servicio_detalle seleccionado
                    # NOTA: En la BD real, el campo 'id_servicio_detalle' en atencion_clinica 
                    # apunta a la tabla 'servicio_detalle'
                    logger.info(f"Guardando servicio_detalle: {servicio_detalle.id_servicio_detalle} - {servicio_detalle.nombre}")
                    
                    atencion = AtencionClinica.objects.create(
                        id_mascota=mascota_encontrada,
                        id_clinica=clinica,
                        id_personal=medico_tratante,
                        id_servicio_detalle=servicio_detalle,  # Guardar directamente el ServicioDetalle
                        fecha_atencion=datetime.strptime(fecha_atencion, '%Y-%m-%d') if fecha_atencion else timezone.now(),
                        peso_kg=peso if peso else None,
                        temperatura_c=temperatura if temperatura else None,
                        motivo=motivo,
                        detalle_clinico=motivo,
                        diagnostico=diagnostico,
                        tratamiento=tratamiento,
                        fecha_registro=timezone.now(),
                        fecha_ultima_actualizacion=None  # Debe quedar nulo según especificación
                    )
                    
                    logger.info(f"Atención creada con ID: {atencion.id_atencion}")
                    
                    # Crear carpeta para documentos adjuntos
                    import os
                    from django.conf import settings
                    
                    directorio_atencion = os.path.join(settings.MEDIA_ROOT, 'Clinicos', str(atencion.id_atencion))
                    os.makedirs(directorio_atencion, exist_ok=True)
                    logger.info(f"Directorio creado: {directorio_atencion}")
                    
                    # Procesar documentos adjuntos
                    documentos_guardados = []
                    logger.info(f"Documentos a procesar: {len(documentos_a_procesar)}")
                    
                    for i, doc_data in enumerate(documentos_a_procesar):
                        archivo = doc_data['archivo']
                        tipo_documento = doc_data['tipo_documento']
                        nombre_documento = doc_data['nombre_documento']
                        
                        logger.info(f"Procesando documento {i+1}: {archivo.name}")
                        
                        # Generar nombre único para el archivo (siguiendo convención del consentimiento)
                        extension = archivo.name.split('.')[-1].lower()
                        fecha = datetime.now().strftime('%Y%m%d')
                        uuid_short = str(uuid.uuid4())[:8]
                        nuevo_nombre = f"doc_{atencion.id_atencion}_{fecha}_{uuid_short}.{extension}"
                        
                        # Guardar archivo en el sistema de archivos
                        ruta_archivo = os.path.join(directorio_atencion, nuevo_nombre)
                        with open(ruta_archivo, 'wb+') as destination:
                            for chunk in archivo.chunks():
                                destination.write(chunk)
                        
                        logger.info(f"Archivo guardado en: {ruta_archivo}")
                        
                        # Crear registro en la base de datos
                        url_relativa = f'Clinicos/{atencion.id_atencion}/{nuevo_nombre}'
                        documento = DocumentoAdjunto.objects.create(
                            id_atencion=atencion,
                            tipo_documento=tipo_documento,
                            nombre_archivo=nombre_documento,
                            url_archivo=url_relativa,
                            fecha_subida=timezone.now(),
                            observaciones=f"Archivo original: {archivo.name}"
                        )
                        
                        documentos_guardados.append(documento)
                        logger.info(f"Documento guardado en BD: {documento}")
                    
                    # Mensaje de éxito
                    num_documentos = len(documentos_guardados)
                    if num_documentos > 0:
                        mensaje_exito = f"Atención médica registrada exitosamente. Se adjuntaron {num_documentos} documento(s)."
                    else:
                        mensaje_exito = "Atención médica registrada exitosamente."
                    
                    atencion_guardada = atencion
                    logger.info(f"Atención médica creada exitosamente: {atencion}")
                    logger.info("=== FIN DE TRANSACCIÓN ===")
                    
                    # Redirigir a la misma página con mensaje de éxito
                    from django.contrib import messages
                    messages.success(request, mensaje_exito)
                    return redirect('atencion_medica:registrar_atencion')
                    
            except Exception as e:
                logger.error(f"Error al registrar atención médica: {e}")
                mensaje_error = f"Error al registrar la atención médica: {str(e)}"
    
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
                return redirect('atencion_medica:registrar_atencion_con_mascota', mascota_id=mascota_encontrada.id_mascota)
                
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
    Filtra por clínica del usuario autenticado.
    
    Flujo:
    1. Obtener ID_Clínica del usuario autenticado
    2. Filtrar Servicio_Detalle por:
       - id_servicio = (Servicio seleccionado)
       - pertenencia a la clínica (existe relación en Clínica_Servicio)
    3. Retornar solo los Servicio_Detalle válidos para esa Clínica y Servicio
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            servicio_id = data.get('servicio_id')
            
            if servicio_id:
                # Obtener la clínica del usuario autenticado
                try:
                    usuario_autenticado = PersonalClinica.objects.get(usuario=1)
                    clinica_id = usuario_autenticado.id_clinica.id_clinica
                    logger.info(f"Clínica del usuario autenticado para AJAX: {clinica_id}")
                except PersonalClinica.DoesNotExist:
                    # Fallback a clínica 1 si no se encuentra el usuario
                    clinica_id = 1
                    logger.warning("Usuario no encontrado en AJAX, usando clínica 1 como fallback")
                
                # Verificar que el servicio existe y está activo
                try:
                    servicio = Servicio.objects.get(id_servicio=servicio_id, activo=True)
                    logger.info(f"Servicio validado: {servicio.id_servicio} - {servicio.nombre}")
                except Servicio.DoesNotExist:
                    logger.error(f"Servicio {servicio_id} no encontrado o no está activo")
                    return JsonResponse({
                        'success': False,
                        'error': 'Servicio no encontrado'
                    })
                
                # Filtrar Servicio_Detalle por clínica y servicio
                # Cruzar Servicio, Clínica_Servicio y Servicio_Detalle
                clinica_servicios = ClinicaServicio.objects.filter(
                    id_clinica=clinica_id,
                    id_servicio_detalle__id_servicio=servicio_id,
                    id_servicio_detalle__activo=True,
                    activo=True
                ).select_related('id_servicio_detalle').order_by('id_servicio_detalle__nombre')
                
                # Extraer solo los servicios detalle disponibles para esta clínica
                servicios_detalle = []
                for cs in clinica_servicios:
                    # Verificar que el servicio detalle existe y está activo
                    if cs.id_servicio_detalle and cs.id_servicio_detalle.activo:
                        servicios_detalle.append({
                            'id_servicio_detalle': cs.id_servicio_detalle.id_servicio_detalle,
                            'nombre': cs.id_servicio_detalle.nombre
                        })
                        logger.info(f"Servicio detalle válido: {cs.id_servicio_detalle.id_servicio_detalle} - {cs.id_servicio_detalle.nombre}")
                
                logger.info(f"Cargando {len(servicios_detalle)} servicios detalle para servicio {servicio_id} en clínica {clinica_id}")
                
                return JsonResponse({
                    'success': True,
                    'servicios_detalle': servicios_detalle
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



