"""
Vista simplificada para registrar mascotas - versión corregida
"""

from django.shortcuts import render
from django.http import JsonResponse, FileResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection, transaction
from core.models import Tutor, Mascota, Especie, Raza, ClinicaVeterinaria, AtencionClinica, DocumentoAdjunto
from .forms import BuscarTutorMascotaForm, RegistrarMascotaForm, BuscarFichaClinicaForm
import json
import logging
import re
import os
import uuid
from datetime import datetime
from django.conf import settings

logger = logging.getLogger(__name__)

def registrar_mascota_view(request):
    """
    Vista simplificada para registrar una nueva mascota.
    """
    logger.info("=== INICIO DE VISTA SIMPLIFICADA ===")
    
    tutor_encontrado = None
    mascota_guardada = None
    mensaje_exito = None
    
    # Verificar si hay parámetro tutor_id en GET (para redirección desde Consultar Tutor)
    tutor_id_get = request.GET.get('tutor_id')
    
    # Formularios
    buscar_tutor_form = BuscarTutorMascotaForm()
    registrar_mascota_form = RegistrarMascotaForm()
    
    # Si hay tutor_id en GET, precargar el tutor
    if tutor_id_get and request.method == 'GET':
        try:
            tutor_encontrado = Tutor.objects.get(id_tutor=tutor_id_get)
            logger.info(f"Tutor precargado desde GET: {tutor_encontrado}")
            # Crear formulario con el RUT precargado
            buscar_tutor_form = BuscarTutorMascotaForm(initial={'rut_tutor': tutor_encontrado.nro_documento})
        except Tutor.DoesNotExist:
            logger.error(f"Tutor con ID {tutor_id_get} no encontrado")
        except (ValueError, TypeError):
            logger.error(f"Tutor ID inválido: {tutor_id_get}")
    
    if request.method == 'POST':
        logger.info("Procesando POST request")
        logger.info(f"Datos POST: {request.POST}")
        logger.info(f"Claves en POST: {list(request.POST.keys())}")
        
        # Determinar qué formulario se está enviando
        if 'buscar_tutor' in request.POST:
            # Búsqueda de tutor
            buscar_tutor_form = BuscarTutorMascotaForm(request.POST)
            
            if buscar_tutor_form.is_valid():
                rut_tutor = buscar_tutor_form.cleaned_data['rut_tutor']
                logger.info(f"Buscando tutor con RUT: {rut_tutor}")
                
                try:
                    tutor_encontrado = Tutor.objects.filter(nro_documento=rut_tutor).first()
                    if tutor_encontrado:
                        logger.info(f"Tutor encontrado: {tutor_encontrado}")
                    else:
                        logger.info("Tutor no encontrado")
                        buscar_tutor_form.add_error('rut_tutor', 'No se encontró un tutor con este RUT')
                
                except Exception as e:
                    logger.error(f"Error al buscar tutor: {e}")
                    buscar_tutor_form.add_error('rut_tutor', 'Error al buscar el tutor')
            
        elif 'registrar_mascota' in request.POST:
            logger.info("=== INICIANDO REGISTRO DE MASCOTA ===")
            # Registro de mascota
            tutor_id = request.POST.get('tutor_id')
            logger.info(f"Tutor ID recibido del formulario: '{tutor_id}' (tipo: {type(tutor_id)})")
            
            # Si tutor_id es una lista, tomar el primer valor no vacío
            if isinstance(tutor_id, list):
                tutor_id = next((tid for tid in tutor_id if tid), None)
                logger.info(f"Tutor ID después de procesar lista: '{tutor_id}'")
            
            # Convertir tutor_id a entero
            try:
                if tutor_id:
                    tutor_id = int(tutor_id)
                    logger.info(f"Tutor ID convertido a entero: {tutor_id}")
                else:
                    logger.error("Tutor ID está vacío o es None")
            except (ValueError, TypeError) as e:
                logger.error(f"Error al convertir tutor_id '{tutor_id}' a entero: {e}")
                tutor_id = None
            
            if tutor_id:
                try:
                    # Buscar tutor
                    tutor_encontrado = Tutor.objects.get(id_tutor=tutor_id)
                    logger.info(f"Tutor encontrado para registro: {tutor_encontrado}")
                    
                    registrar_mascota_form = RegistrarMascotaForm(request.POST, request.FILES)
                    
                    # Configurar queryset de razas si se seleccionó especie
                    if 'especie' in request.POST and request.POST['especie']:
                        especie_id = request.POST['especie']
                        registrar_mascota_form.fields['raza'].queryset = Raza.objects.filter(
                            id_especie=especie_id, activo=True
                        ).order_by('nombre')
                    
                    if registrar_mascota_form.is_valid():
                        logger.info("Formulario válido, procediendo a crear mascota")
                        logger.info(f"Tutor para crear mascota: {tutor_encontrado}")
                        
                        try:
                            # Usar transacción explícita
                            with transaction.atomic():
                                logger.info("=== INICIANDO TRANSACCIÓN ATOMIC ===")
                                
                                # Determinar consentimiento y procesar archivo
                                tiene_consentimiento = bool(registrar_mascota_form.cleaned_data.get('documento_consentimiento'))
                                fecha_consentimiento = datetime.now().date() if tiene_consentimiento else None
                                url_doc_consentimiento = ''
                                
                                # Asignar clínica de consentimiento solo si existe documento
                                if tiene_consentimiento:
                                    clinica_consentimiento = ClinicaVeterinaria.objects.get(id_clinica=1)
                                    logger.info(f"Documento de consentimiento presente. Clínica asignada: {clinica_consentimiento}")
                                    
                                    # Procesar el archivo adjunto
                                    archivo_consentimiento = registrar_mascota_form.cleaned_data['documento_consentimiento']
                                    
                                    # Validar tipo de archivo
                                    tipos_permitidos = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']
                                    if archivo_consentimiento.content_type not in tipos_permitidos:
                                        raise ValueError('Tipo de archivo no permitido. Solo se aceptan PDF, JPG, JPEG y PNG')
                                    
                                    # Validar tamaño (máximo 10MB)
                                    if archivo_consentimiento.size > 10 * 1024 * 1024:
                                        raise ValueError('El archivo es demasiado grande. Máximo 10MB')
                                    
                                    # Generar nombre único para el archivo
                                    extension = archivo_consentimiento.name.split('.')[-1].lower()
                                    fecha = datetime.now().strftime('%Y%m%d')
                                    uuid_short = str(uuid.uuid4())[:8]
                                    nombre_archivo = f"consent_{registrar_mascota_form.cleaned_data['nro_chip']}_{fecha}_{uuid_short}.{extension}"
                                    
                                    # Crear directorio si no existe
                                    directorio = os.path.join(settings.MEDIA_ROOT, 'consentimientos', str(tutor_encontrado.id_tutor))
                                    os.makedirs(directorio, exist_ok=True)
                                    
                                    # Guardar archivo
                                    ruta_archivo = os.path.join(directorio, nombre_archivo)
                                    with open(ruta_archivo, 'wb+') as destino:
                                        for chunk in archivo_consentimiento.chunks():
                                            destino.write(chunk)
                                    
                                    # Generar URL relativa
                                    url_doc_consentimiento = f'consentimientos/{tutor_encontrado.id_tutor}/{nombre_archivo}'
                                    logger.info(f"Archivo de consentimiento guardado: {url_doc_consentimiento}")
                                else:
                                    clinica_consentimiento = None
                                    logger.info("No hay documento de consentimiento. Clínica asignada: None")
                                
                                # Convertir estado_reproductivo a boolean
                                estado_reproductivo_raw = registrar_mascota_form.cleaned_data['estado_reproductivo']
                                estado_reproductivo_boolean = estado_reproductivo_raw == 'True' if estado_reproductivo_raw else False
                                
                                # Determinar el número de chip según el tipo de identificación
                                tipo_identificacion = registrar_mascota_form.cleaned_data['tipo_identificacion']
                                if tipo_identificacion == 'EXTERNO':
                                    # Para identificación externa, el campo nro_chip queda NULL
                                    nro_chip = None
                                else:
                                    # Para identificación interna, usar el valor del formulario
                                    nro_chip = registrar_mascota_form.cleaned_data['nro_chip']
                                
                                # Crear la mascota
                                mascota = Mascota.objects.create(
                                    id_tutor=tutor_encontrado,
                                    id_especie=registrar_mascota_form.cleaned_data['especie'],
                                    id_raza=registrar_mascota_form.cleaned_data['raza'],
                                    nombre=registrar_mascota_form.cleaned_data['nombre'],
                                    tipo_identificacion=tipo_identificacion,
                                    nro_chip=nro_chip,
                                    sexo=registrar_mascota_form.cleaned_data['sexo'].upper(),
                                    color=registrar_mascota_form.cleaned_data['color'] or '',
                                    patron=registrar_mascota_form.cleaned_data['patron'] or '',
                                    fecha_nacimiento=registrar_mascota_form.cleaned_data['fecha_nacimiento'],
                                    estado_reproductivo=estado_reproductivo_boolean,
                                    modo_obtencion=registrar_mascota_form.cleaned_data.get('modo_obtencion', '').upper() or '',
                                    razon_tenencia=registrar_mascota_form.cleaned_data.get('razon_tenencia', '').upper() or '',
                                    notas_adicionales=registrar_mascota_form.cleaned_data['notas_adicionales'] or '',
                                    estado_vital='VIVO',
                                    consentimiento=tiene_consentimiento,
                                    fecha_consentimiento=fecha_consentimiento,
                                    id_clinica_consentimiento=clinica_consentimiento,  # Usar instancia
                                    url_doc_consentimiento=url_doc_consentimiento,
                                    foto='',
                                    fecha_registro=datetime.now()
                                )
                                
                                logger.info(f"Mascota creada exitosamente. ID: {mascota.id_mascota}")
                                logger.info("=== FIN TRANSACCIÓN ATOMIC ===")
                                
                                mascota_guardada = mascota
                                mensaje_exito = f"La mascota '{mascota.nombre}' ha sido registrada exitosamente"
                                
                                # Limpiar formularios
                                buscar_tutor_form = BuscarTutorMascotaForm()
                                registrar_mascota_form = RegistrarMascotaForm()
                                tutor_encontrado = None
                                
                        except Exception as e:
                            logger.error(f"Error al crear mascota: {e}")
                            logger.error(f"Tipo de error: {type(e).__name__}")
                            registrar_mascota_form.add_error(None, f"Error al guardar la mascota: {str(e)}")
                    else:
                        logger.info("Formulario no válido")
                        logger.info(f"Errores: {registrar_mascota_form.errors}")
                
                except Tutor.DoesNotExist:
                    logger.error(f"Tutor con ID {tutor_id} no encontrado")
                    registrar_mascota_form.add_error(None, "Tutor no válido. Por favor, busque nuevamente.")
                except Exception as e:
                    logger.error(f"Error inesperado: {e}")
                    registrar_mascota_form.add_error(None, f"Error inesperado: {str(e)}")
            else:
                logger.error("No se pudo obtener un tutor_id válido")
                registrar_mascota_form = RegistrarMascotaForm(request.POST, request.FILES)
                registrar_mascota_form.add_error(None, "Error: No se pudo identificar el tutor. Por favor, busque el tutor nuevamente.")
    
    logger.info(f"Tutor encontrado: {tutor_encontrado}")
    logger.info(f"Mascota guardada: {mascota_guardada}")
    logger.info("=== FIN DE VISTA SIMPLIFICADA ===")
    
    context = {
        'buscar_tutor_form': buscar_tutor_form,
        'registrar_mascota_form': registrar_mascota_form,
        'tutor_encontrado': tutor_encontrado,
        'mascota_guardada': mascota_guardada,
        'mensaje_exito': mensaje_exito,
    }
    
    logger.info(f"Context enviado al template: {context}")
    
    return render(request, 'mascotas/registrar_mascota.html', context)


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


@csrf_exempt
def validar_chip(request):
    """
    Vista AJAX para validar si un número de chip ya existe en el sistema.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nro_chip = data.get('nro_chip', '').strip()
            
            if not nro_chip:
                return JsonResponse({
                    'success': False,
                    'error': 'El número de chip es obligatorio'
                })
            
            # Verificar si el chip ya existe
            chip_existe = Mascota.objects.filter(nro_chip=nro_chip).exists()
            
            if chip_existe:
                # Obtener información de la mascota existente
                mascota_existente = Mascota.objects.filter(nro_chip=nro_chip).first()
                return JsonResponse({
                    'success': False,
                    'chip_existe': True,
                    'nro_chip': nro_chip,
                    'mensaje': f'Ya existe una mascota registrada en el sistema asociada al número de chip: {nro_chip}',
                    'mascota_info': {
                        'nombre': mascota_existente.nombre,
                        'tutor': f"{mascota_existente.id_tutor.nombres} {mascota_existente.id_tutor.apellido_paterno}",
                        'especie': mascota_existente.id_especie.nombre,
                        'raza': mascota_existente.id_raza.nombre
                    }
                })
            else:
                return JsonResponse({
                    'success': True,
                    'chip_existe': False,
                    'mensaje': 'El número de chip está disponible'
                })
                
        except Exception as e:
            logger.error(f"Error al validar chip: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Error al validar el número de chip'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    })


def ficha_clinica_view(request):
    """
    Vista para mostrar la ficha clínica de una mascota.
    """
    mascota_encontrada = None
    historial_atenciones = []
    mensaje = None
    
    # Verificar si hay parámetros en GET (para redirección desde otros formularios)
    nro_chip_get = request.GET.get('nro_chip')
    id_mascota_get = request.GET.get('id_mascota')
    
    if request.method == 'POST':
        # Verificar si se está enviando mascota_id desde el modal
        mascota_id = request.POST.get('mascota_id')
        
        if mascota_id:
            # Búsqueda por ID de mascota (desde modal)
            try:
                mascota_encontrada = Mascota.objects.get(id_mascota=mascota_id)
                historial_atenciones = AtencionClinica.objects.filter(
                    id_mascota=mascota_encontrada
                ).order_by('-fecha_atencion')
                form = BuscarFichaClinicaForm()  # Formulario vacío ya que no se usa
            except Mascota.DoesNotExist:
                mensaje = f"No se encontró la mascota con ID: {mascota_id}"
                form = BuscarFichaClinicaForm()
        else:
            # Búsqueda por microchip (formulario original)
            form = BuscarFichaClinicaForm(request.POST)
            
            if form.is_valid():
                nro_chip = form.cleaned_data['nro_chip']
                try:
                    mascota_encontrada = Mascota.objects.get(nro_chip=nro_chip)
                    historial_atenciones = AtencionClinica.objects.filter(
                        id_mascota=mascota_encontrada
                    ).order_by('-fecha_atencion')
                except Mascota.DoesNotExist:
                    mensaje = f"No se encontraron registros para este número de chip: {nro_chip}"
    else:
        # Si hay parámetros en GET, precargar la búsqueda
        if id_mascota_get:
            # Priorizar búsqueda por ID de mascota
            try:
                mascota_encontrada = Mascota.objects.get(id_mascota=id_mascota_get)
                historial_atenciones = AtencionClinica.objects.filter(
                    id_mascota=mascota_encontrada
                ).order_by('-fecha_atencion')
                # Crear formulario vacío ya que no se usa el campo de búsqueda
                form = BuscarFichaClinicaForm()
            except Mascota.DoesNotExist:
                mensaje = f"No se encontró la mascota con ID: {id_mascota_get}"
                form = BuscarFichaClinicaForm()
            except (ValueError, TypeError):
                mensaje = f"ID de mascota inválido: {id_mascota_get}"
                form = BuscarFichaClinicaForm()
        elif nro_chip_get:
            # Búsqueda por número de chip (mantener compatibilidad)
            try:
                mascota_encontrada = Mascota.objects.get(nro_chip=nro_chip_get)
                historial_atenciones = AtencionClinica.objects.filter(
                    id_mascota=mascota_encontrada
                ).order_by('-fecha_atencion')
                # Crear formulario con el nro_chip precargado
                form = BuscarFichaClinicaForm(initial={'nro_chip': nro_chip_get})
            except Mascota.DoesNotExist:
                mensaje = f"No se encontraron registros para este número de chip: {nro_chip_get}"
                form = BuscarFichaClinicaForm()
        else:
            form = BuscarFichaClinicaForm()
    
    return render(request, 'mascotas/ficha_clinica.html', {
        'form': form,
        'mascota_encontrada': mascota_encontrada,
        'historial_atenciones': historial_atenciones,
        'mensaje': mensaje,
    })


def ver_consentimiento(request, mascota_id):
    """
    Vista para ver información del consentimiento de una mascota.
    """
    try:
        mascota = Mascota.objects.get(id_mascota=mascota_id)
        
        if mascota.consentimiento and mascota.url_doc_consentimiento:
            nombre_archivo = mascota.url_doc_consentimiento.split('/')[-1]
            
            return JsonResponse({
                'success': True,
                'existe_documento': True,
                'documento': {
                    'id': mascota.id_mascota,
                    'nombre': nombre_archivo,
                    'tipo': 'Consentimiento de Interoperabilidad',
                    'fecha_subida': mascota.fecha_consentimiento.strftime('%d/%m/%Y') if mascota.fecha_consentimiento else None,
                    'url': mascota.url_doc_consentimiento
                }
            })
        else:
            return JsonResponse({
                'success': True,
                'existe_documento': False,
                'consentimiento': mascota.consentimiento
            })
            
    except Mascota.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Mascota no encontrada'
        })
    except Exception as e:
        logger.error(f"Error al ver consentimiento: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Error al obtener información del consentimiento'
        })


@csrf_exempt
def subir_consentimiento(request, mascota_id):
    """
    Vista para subir un documento de consentimiento.
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Método no permitido'
        })
    
    try:
        mascota = Mascota.objects.get(id_mascota=mascota_id)
        
        if 'documento' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No se ha seleccionado ningún archivo'
            })
        
        archivo = request.FILES['documento']
        
        # Validar tipo de archivo
        tipos_permitidos = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']
        if archivo.content_type not in tipos_permitidos:
            return JsonResponse({
                'success': False,
                'error': 'Tipo de archivo no permitido. Solo se aceptan PDF, JPG, JPEG y PNG'
            })
        
        # Validar tamaño (máximo 10MB)
        if archivo.size > 10 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': 'El archivo es demasiado grande. Máximo 10MB'
            })
        
        # Generar nombre único para el archivo
        import uuid
        extension = archivo.name.split('.')[-1].lower()
        fecha = datetime.now().strftime('%Y%m%d')
        uuid_short = str(uuid.uuid4())[:8]
        nombre_archivo = f"consent_{mascota.nro_chip}_{fecha}_{uuid_short}.{extension}"
        
        # Guardar archivo en el sistema de archivos
        directorio = os.path.join(settings.MEDIA_ROOT, 'consentimientos', str(mascota.id_tutor.id_tutor))
        os.makedirs(directorio, exist_ok=True)
        
        ruta_archivo = os.path.join(directorio, nombre_archivo)
        
        with open(ruta_archivo, 'wb+') as destino:
            for chunk in archivo.chunks():
                destino.write(chunk)
        
        # Actualizar consentimiento de la mascota
        url_relativa = f'consentimientos/{mascota.id_tutor.id_tutor}/{nombre_archivo}'
        
        # Obtener la clínica con ID 1
        clinica = ClinicaVeterinaria.objects.get(id_clinica=1)
        
        mascota.consentimiento = True
        mascota.fecha_consentimiento = datetime.now().date()
        mascota.url_doc_consentimiento = url_relativa
        mascota.id_clinica_consentimiento = clinica
        mascota.save()
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Documento de consentimiento subido exitosamente',
            'clinica_consentimiento': clinica.nombre,
            'fecha_consentimiento': mascota.fecha_consentimiento.strftime('%d/%m/%Y'),
            'documento': {
                'id': mascota.id_mascota,
                'nombre': archivo.name,
                'url': url_relativa
            }
        })
        
    except Mascota.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Mascota no encontrada'
        })
    except Exception as e:
        logger.error(f"Error al subir consentimiento: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Error al subir el documento'
        })


def descargar_consentimiento(request, documento_id):
    """
    Vista para descargar un documento de consentimiento.
    """
    try:
        mascota = Mascota.objects.get(id_mascota=documento_id)
        
        if not mascota.consentimiento or not mascota.url_doc_consentimiento:
            return JsonResponse({
                'success': False,
                'error': 'No existe documento de consentimiento para esta mascota'
            })
        
        ruta_archivo = os.path.join(settings.MEDIA_ROOT, mascota.url_doc_consentimiento)
        
        if os.path.exists(ruta_archivo):
            nombre_archivo = mascota.url_doc_consentimiento.split('/')[-1]
            
            response = FileResponse(open(ruta_archivo, 'rb'))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
            return response
        else:
            return JsonResponse({
                'success': False,
                'error': 'Archivo no encontrado'
            })
            
    except Mascota.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Mascota no encontrada'
        })
    except Exception as e:
        logger.error(f"Error al descargar consentimiento: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Error al descargar el documento'
        })


def ver_consentimiento_pdf(request, documento_id):
    """
    Vista para mostrar PDFs de consentimiento en el navegador.
    """
    try:
        mascota = Mascota.objects.get(id_mascota=documento_id)
        
        if not mascota.consentimiento or not mascota.url_doc_consentimiento:
            return HttpResponse("No existe documento de consentimiento para esta mascota", status=404)
        
        ruta_archivo = os.path.join(settings.MEDIA_ROOT, mascota.url_doc_consentimiento)
        
        if os.path.exists(ruta_archivo):
            extension = os.path.splitext(mascota.url_doc_consentimiento)[1].lower()
            
            if extension == '.pdf':
                content_type = 'application/pdf'
            elif extension in ['.jpg', '.jpeg']:
                content_type = 'image/jpeg'
            elif extension == '.png':
                content_type = 'image/png'
            else:
                content_type = 'application/octet-stream'
            
            response = FileResponse(open(ruta_archivo, 'rb'))
            response['Content-Type'] = content_type
            response['Content-Disposition'] = 'inline'
            return response
        else:
            return HttpResponse("Archivo no encontrado", status=404)
            
    except Mascota.DoesNotExist:
        return HttpResponse("Mascota no encontrada", status=404)
    except Exception as e:
        logger.error(f"Error al ver consentimiento PDF: {e}")
        return HttpResponse("Error al mostrar el documento", status=500)


def atencion_detalle_view(request, atencion_id):
    """
    Vista para mostrar el detalle completo de una atención médica.
    """
    try:
        atencion = AtencionClinica.objects.get(id_atencion=atencion_id)
        documentos = DocumentoAdjunto.objects.filter(id_atencion=atencion).order_by('fecha_subida')
        
        return render(request, 'mascotas/atencion_detalle.html', {
            'atencion': atencion,
            'documentos': documentos,
            'insumos': [],  # Simplificado por ahora
        })
        
    except AtencionClinica.DoesNotExist:
        logger.error(f"Atención con ID {atencion_id} no encontrada")
        return render(request, 'mascotas/atencion_detalle.html', {
            'error': 'La atención médica no fue encontrada'
        })
    except Exception as e:
        logger.error(f"Error al cargar detalle de atención {atencion_id}: {e}")
        return render(request, 'mascotas/atencion_detalle.html', {
            'error': 'Error al cargar los detalles de la atención médica'
        })


def descargar_documento_atencion(request, documento_id):
    """
    Vista para descargar un documento adjunto de una atención médica.
    """
    try:
        documento = DocumentoAdjunto.objects.get(id_documento=documento_id)
        
        if not documento.url_archivo:
            return JsonResponse({
                'success': False,
                'error': 'No existe archivo asociado a este documento'
            })
        
        ruta_archivo = os.path.join(settings.MEDIA_ROOT, documento.url_archivo)
        
        if os.path.exists(ruta_archivo):
            response = FileResponse(open(ruta_archivo, 'rb'))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = f'attachment; filename="{documento.nombre_archivo}"'
            return response
        else:
            return JsonResponse({
                'success': False,
                'error': 'Archivo no encontrado'
            })
            
    except DocumentoAdjunto.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Documento no encontrado'
        })
    except Exception as e:
        logger.error(f"Error al descargar documento {documento_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Error al descargar el documento'
        })


def ver_documento_atencion(request, documento_id):
    """
    Vista para mostrar documentos de atención médica en el navegador.
    """
    try:
        documento = DocumentoAdjunto.objects.get(id_documento=documento_id)
        
        if not documento.url_archivo:
            return HttpResponse("No existe archivo asociado a este documento", status=404)
        
        ruta_archivo = os.path.join(settings.MEDIA_ROOT, documento.url_archivo)
        
        if os.path.exists(ruta_archivo):
            extension = os.path.splitext(documento.url_archivo)[1].lower()
            
            if extension == '.pdf':
                content_type = 'application/pdf'
            elif extension in ['.jpg', '.jpeg']:
                content_type = 'image/jpeg'
            elif extension == '.png':
                content_type = 'image/png'
            else:
                content_type = 'application/octet-stream'
            
            response = FileResponse(open(ruta_archivo, 'rb'))
            response['Content-Type'] = content_type
            response['Content-Disposition'] = 'inline'
            return response
        else:
            return HttpResponse("Archivo no encontrado", status=404)
            
    except DocumentoAdjunto.DoesNotExist:
        return HttpResponse("Documento no encontrado", status=404)
    except Exception as e:
        logger.error(f"Error al ver documento {documento_id}: {e}")
        return HttpResponse("Error al mostrar el documento", status=500)


@csrf_exempt
def validar_mascota_duplicada(request):
    """
    Vista para validar si existe una mascota con las mismas características:
    tutor + especie + nombre + fecha de nacimiento
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Método no permitido'
        })
    
    try:
        # Parsear datos JSON
        data = json.loads(request.body)
        tutor_id = data.get('tutor_id')
        especie_id = data.get('especie_id')
        nombre = data.get('nombre', '').strip()
        sexo = data.get('sexo')
        
        # Validar que tengamos todos los datos necesarios
        if not all([tutor_id, especie_id, nombre, sexo]):
            return JsonResponse({
                'success': False,
                'error': 'Faltan datos requeridos para la validación'
            })
        
        # Convertir IDs a enteros
        try:
            tutor_id = int(tutor_id)
            especie_id = int(especie_id)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'IDs inválidos'
            })
        
        # Buscar mascota con las mismas características
        logger.info(f"Buscando mascota con: tutor_id={tutor_id}, especie_id={especie_id}, nombre='{nombre}', sexo='{sexo}'")
        
        mascota_existente = Mascota.objects.filter(
            id_tutor=tutor_id,
            id_especie=especie_id,
            nombre__iexact=nombre,  # Búsqueda case-insensitive
            sexo=sexo.upper()  # Convertir a mayúsculas para consistencia
        ).first()
        
        logger.info(f"Mascota encontrada: {mascota_existente}")
        
        if mascota_existente:
            # Obtener información de la mascota existente para mostrar en el modal
            try:
                mascota_info = {
                    'nombre': mascota_existente.nombre,
                    'tutor': f"{mascota_existente.id_tutor.nombres} {mascota_existente.id_tutor.apellido_paterno}",
                    'especie': mascota_existente.id_especie.nombre,
                    'sexo': mascota_existente.sexo if mascota_existente.sexo else 'No especificado'
                }
            except Exception as e:
                logger.error(f"Error al obtener información de mascota existente: {e}")
                mascota_info = None
            
            logger.info(f"Enviando respuesta con mascota_info: {mascota_info}")
            return JsonResponse({
                'success': True,
                'mascota_existe': True,
                'mascota_info': mascota_info
            })
        else:
            return JsonResponse({
                'success': True,
                'mascota_existe': False
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Datos JSON inválidos'
        })
    except Exception as e:
        logger.error(f"Error en validar_mascota_duplicada: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Error interno del servidor'
        })


@csrf_exempt
def buscar_mascotas_por_tutor(request):
    """
    Vista AJAX para buscar mascotas asociadas a un tutor por RUT
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Método no permitido'
        })
    
    try:
        # Parsear datos JSON
        data = json.loads(request.body)
        rut_tutor = data.get('rut_tutor', '').strip()
        
        # Validar que tengamos el RUT
        if not rut_tutor:
            return JsonResponse({
                'success': False,
                'error': 'RUT del tutor es requerido'
            })
        
        logger.info(f"Buscando mascotas para tutor con RUT: {rut_tutor}")
        
        # Buscar tutor por RUT
        tutor = Tutor.objects.filter(nro_documento=rut_tutor).first()
        
        if not tutor:
            return JsonResponse({
                'success': False,
                'error': 'No se encontró un tutor con este RUT'
            })
        
        # Buscar mascotas asociadas al tutor
        mascotas = Mascota.objects.filter(id_tutor=tutor).select_related('id_especie')
        
        logger.info(f"Encontradas {mascotas.count()} mascotas para el tutor {tutor}")
        
        # Preparar datos de mascotas para JSON
        mascotas_data = []
        for mascota in mascotas:
            mascota_info = {
                'id_mascota': mascota.id_mascota,
                'nro_chip': mascota.nro_chip,
                'nombre': mascota.nombre,
                'especie': mascota.id_especie.nombre if mascota.id_especie else 'No especificada',
                'sexo': mascota.sexo if mascota.sexo else 'No especificado',
                'estado_vital': mascota.estado_vital if mascota.estado_vital else 'No especificado'
            }
            mascotas_data.append(mascota_info)
        
        return JsonResponse({
            'success': True,
            'mascotas': mascotas_data,
            'total_mascotas': len(mascotas_data)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Datos JSON inválidos'
        })
    except Exception as e:
        logger.error(f"Error en buscar_mascotas_por_tutor: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Error interno del servidor'
        })
