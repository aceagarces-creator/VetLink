"""
Vistas para la gestión de mascotas.

Este módulo contiene las vistas para la gestión de mascotas,
incluyendo registro de nuevas mascotas y búsqueda de tutores.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from core.models import Tutor, Mascota, Especie, Raza, ClinicaVeterinaria, Servicio, ServicioDetalle, PersonalClinica, AtencionClinica, DocumentoAdjunto
from .forms import BuscarTutorMascotaForm, RegistrarMascotaForm, BuscarFichaClinicaForm
import json
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)


def verificar_secuencia_mascota():
    """
    Verifica el estado de la secuencia de mascota en PostgreSQL.
    """
    try:
        with connection.cursor() as cursor:
            # Verificar si la secuencia existe usando información_schema
            cursor.execute("""
                SELECT sequence_name, data_type, start_value, minimum_value, maximum_value, increment
                FROM information_schema.sequences 
                WHERE sequence_name = 'mascota_id_mascota_seq'
            """)
            result = cursor.fetchone()
            
            if result:
                sequence_name, data_type, start_value, min_value, max_value, increment = result
                logger.info(f"Secuencia encontrada: {sequence_name}")
                logger.info(f"Tipo de datos: {data_type}")
                logger.info(f"Valor inicial: {start_value}")
                logger.info(f"Valor mínimo: {min_value}")
                logger.info(f"Valor máximo: {max_value}")
                logger.info(f"Incremento: {increment}")
                
                # Verificar el valor actual de la secuencia
                cursor.execute("SELECT last_value, is_called FROM mascota_id_mascota_seq")
                seq_result = cursor.fetchone()
                if seq_result:
                    last_value, is_called = seq_result
                    logger.info(f"Último valor de la secuencia: {last_value}")
                    logger.info(f"Secuencia ha sido llamada: {is_called}")
                
                return True
            else:
                logger.warning("Secuencia mascota_id_mascota_seq no encontrada en information_schema")
                
                # Intentar verificar directamente la secuencia
                try:
                    cursor.execute("SELECT last_value FROM mascota_id_mascota_seq")
                    last_value = cursor.fetchone()[0]
                    logger.info(f"Secuencia encontrada directamente, último valor: {last_value}")
                    return True
                except Exception as e:
                    logger.error(f"No se puede acceder a la secuencia: {e}")
                    return False
                
    except Exception as e:
        logger.error(f"Error al verificar secuencia: {e}")
        return False


def probar_insercion_directa(tutor_encontrado, datos_mascota):
    """
    Prueba la inserción directa con SQL para verificar si hay problemas con la secuencia.
    """
    try:
        with connection.cursor() as cursor:
            # Construir la consulta SQL directa
            sql = """
                INSERT INTO mascota (
                    id_tutor, id_especie, id_raza, nombre, nro_chip, sexo, 
                    color, fecha_nacimiento, estado_reproductivo, notas_adicionales,
                    estado_vital, consentimiento, fecha_consentimiento, 
                    url_doc_consentimiento, foto, fecha_registro
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) RETURNING id_mascota
            """
            
            valores = (
                tutor_encontrado.id_tutor,
                datos_mascota['especie'].id_especie,
                datos_mascota['raza'].id_raza,
                datos_mascota['nombre'],
                datos_mascota['nro_chip'],
                datos_mascota['sexo'],
                datos_mascota['color'] or '',
                datos_mascota['fecha_nacimiento'],
                datos_mascota['estado_reproductivo'] or '',
                datos_mascota['notas_adicionales'] or '',
                'Vivo',
                bool(datos_mascota['documento_consentimiento']),
                datetime.now().date() if datos_mascota['documento_consentimiento'] else None,
                '',
                '',
                datetime.now()
            )
            
            cursor.execute(sql, valores)
            id_generado = cursor.fetchone()[0]
            
            logger.info(f"Inserción directa exitosa. ID generado: {id_generado}")
            return id_generado
            
    except Exception as e:
        logger.error(f"Error en inserción directa: {e}")
        return None


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
    
    # Verificar si hay parámetros GET para precargar datos del tutor
    if request.method == 'GET' and 'tutor_id' in request.GET:
        tutor_id = request.GET.get('tutor_id')
        try:
            tutor_encontrado = Tutor.objects.get(id_tutor=tutor_id)
            logger.info(f"Tutor precargado desde GET: {tutor_encontrado}")
            
            # Precargar el formulario de búsqueda de tutor
            buscar_tutor_form = BuscarTutorMascotaForm(initial={'rut_tutor': tutor_encontrado.nro_documento})
            
            # Precargar el formulario de registro de mascota
            registrar_mascota_form = RegistrarMascotaForm(tutor_id=tutor_encontrado.id_tutor, initial={'tutor_id': tutor_encontrado.id_tutor})
            
        except Tutor.DoesNotExist:
            logger.error(f"Tutor con ID {tutor_id} no encontrado en GET")
    
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
                
                # Buscar tutor por RUT completo (con DV)
                try:
                    tutor_encontrado = Tutor.objects.filter(nro_documento=rut_tutor).first()
                    if tutor_encontrado:
                        logger.info(f"Tutor encontrado: {tutor_encontrado}")
                    else:
                        logger.info("Tutor no encontrado")
                    
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
                            # Verificar el estado de la secuencia antes de crear la mascota
                            logger.info("Verificando estado de la secuencia de mascota...")
                            secuencia_ok = verificar_secuencia_mascota()
                            
                            if not secuencia_ok:
                                logger.warning("Problema detectado con la secuencia de mascota")
                            
                            # Crear la mascota sin asignar manualmente el id_mascota
                            # Django automáticamente usará la secuencia PostgreSQL
                            logger.info("Iniciando creación de mascota sin asignar id_mascota manualmente")
                            
                            try:
                                # Intentar con Django ORM primero
                                mascota = Mascota.objects.create(
                                    # NO asignar id_mascota - se usará la secuencia automática
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
                                
                                logger.info(f"Mascota creada exitosamente con Django ORM. ID automático: {mascota.id_mascota}")
                                
                            except Exception as orm_error:
                                logger.warning(f"Error con Django ORM: {orm_error}")
                                logger.info("Intentando inserción directa con SQL...")
                                
                                # Intentar inserción directa como respaldo
                                id_generado = probar_insercion_directa(tutor_encontrado, registrar_mascota_form.cleaned_data)
                                
                                if id_generado:
                                    # Recuperar la mascota creada
                                    mascota = Mascota.objects.get(id_mascota=id_generado)
                                    logger.info(f"Mascota creada exitosamente con SQL directo. ID: {id_generado}")
                                else:
                                    raise Exception("No se pudo crear la mascota ni con ORM ni con SQL directo")
                            
                            mascota_guardada = mascota
                            mensaje_exito = f"La mascota '{mascota.nombre}' ha sido registrada exitosamente"
                            
                            # Limpiar formularios para nuevo registro
                            buscar_tutor_form = BuscarTutorMascotaForm()
                            registrar_mascota_form = RegistrarMascotaForm()
                            tutor_encontrado = None
                            
                        except Exception as e:
                            logger.error(f"Error al crear mascota: {e}")
                            logger.error(f"Tipo de error: {type(e).__name__}")
                            logger.error(f"Detalles del error: {str(e)}")
                            registrar_mascota_form.add_error(None, f"Error al guardar la mascota: {str(e)}")
                    
                    else:
                        logger.info("Formulario de mascota no válido")
                        logger.info(f"Errores del formulario: {registrar_mascota_form.errors}")
                        logger.info(f"Errores de campos específicos:")
                        for field, errors in registrar_mascota_form.errors.items():
                            logger.info(f"  {field}: {errors}")
                
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
    Vista para mostrar la ficha clínica de una mascota buscada por número de chip.
    Incluye antecedentes del tutor, datos de la mascota e historial de atenciones médicas.
    """
    mascota_encontrada = None
    historial_atenciones = []
    mensaje = None
    
    logger.info(f"Método de request: {request.method}")
    
    # Verificar si hay parámetro nro_chip en GET (viene desde Consultar Tutor)
    nro_chip_get = request.GET.get('nro_chip')
    
    if request.method == 'POST':
        form = BuscarFichaClinicaForm(request.POST)
        
        if form.is_valid():
            nro_chip = form.cleaned_data['nro_chip']
            logger.info(f"Buscando mascota con chip desde formulario: {nro_chip}")
            
            try:
                # Buscar mascota por número de chip
                mascota_encontrada = Mascota.objects.select_related(
                    'id_tutor',
                    'id_tutor__id_comuna',
                    'id_tutor__id_comuna__id_provincia', 
                    'id_tutor__id_comuna__id_provincia__id_region',
                    'id_especie',
                    'id_raza',
                    'id_clinica_consentimiento'
                ).get(nro_chip=nro_chip)
                
                logger.info(f"Mascota encontrada: {mascota_encontrada}")
                
                # Obtener historial de atenciones médicas ordenado por fecha más reciente
                historial_atenciones = AtencionClinica.objects.filter(
                    id_mascota=mascota_encontrada
                ).select_related(
                    'id_clinica',
                    'id_personal',
                    'id_servicio_detalle',
                    'id_servicio_detalle__id_servicio'
                ).order_by('-fecha_atencion')
                
                logger.info(f"Encontradas {historial_atenciones.count()} atenciones")
                
            except Mascota.DoesNotExist:
                mensaje = f"No se encontraron registros para este número de chip: {nro_chip}"
                logger.info(f"Mascota no encontrada con chip: {nro_chip}")
        else:
            logger.info("Formulario no válido")
            logger.info(f"Errores del formulario: {form.errors}")
    elif nro_chip_get:
        # Búsqueda automática desde Consultar Tutor
        logger.info(f"Buscando mascota con chip desde GET: {nro_chip_get}")
        
        try:
            # Buscar mascota por número de chip
            mascota_encontrada = Mascota.objects.select_related(
                'id_tutor',
                'id_tutor__id_comuna',
                'id_tutor__id_comuna__id_provincia', 
                'id_tutor__id_comuna__id_provincia__id_region',
                'id_especie',
                'id_raza',
                'id_clinica_consentimiento'
            ).get(nro_chip=nro_chip_get)
            
            logger.info(f"Mascota encontrada: {mascota_encontrada}")
            
            # Obtener historial de atenciones médicas ordenado por fecha más reciente
            historial_atenciones = AtencionClinica.objects.filter(
                id_mascota=mascota_encontrada
            ).select_related(
                'id_clinica',
                'id_personal',
                'id_servicio_detalle',
                'id_servicio_detalle__id_servicio'
            ).order_by('-fecha_atencion')
            
            logger.info(f"Encontradas {historial_atenciones.count()} atenciones")
            
            # Crear formulario precargado con el chip
            form = BuscarFichaClinicaForm(initial={'nro_chip': nro_chip_get})
            
        except Mascota.DoesNotExist:
            mensaje = f"No se encontraron registros para este número de chip: {nro_chip_get}"
            logger.info(f"Mascota no encontrada con chip: {nro_chip_get}")
            form = BuscarFichaClinicaForm()
    else:
        form = BuscarFichaClinicaForm()
    
    logger.info(f"Mascota encontrada: {mascota_encontrada}")
    logger.info(f"Historial atenciones: {len(historial_atenciones) if historial_atenciones else 0}")
    
    return render(request, 'mascotas/ficha_clinica.html', {
        'form': form,
        'mascota_encontrada': mascota_encontrada,
        'historial_atenciones': historial_atenciones,
        'mensaje': mensaje,
    })


def atencion_detalle_view(request, atencion_id):
    """
    Vista para mostrar el detalle completo de una atención médica específica.
    Incluye información del tutor, mascota, atención y documentos adjuntos.
    """
    try:
        # Obtener la atención clínica con todas las relaciones necesarias
        atencion = AtencionClinica.objects.select_related(
            'id_mascota',
            'id_mascota__id_tutor',
            'id_mascota__id_tutor__id_comuna',
            'id_mascota__id_tutor__id_comuna__id_provincia',
            'id_mascota__id_tutor__id_comuna__id_provincia__id_region',
            'id_mascota__id_especie',
            'id_mascota__id_raza',
            'id_clinica',
            'id_personal',
            'id_servicio_detalle',
            'id_servicio_detalle__id_servicio'
        ).get(id_atencion=atencion_id)
        
        # Obtener documentos adjuntos asociados a esta atención
        documentos_adjuntos = atencion.documentoadjunto_set.all().order_by('fecha_subida')
        
        logger.info(f"Detalle de atención cargado: {atencion}")
        logger.info(f"Documentos adjuntos encontrados: {documentos_adjuntos.count()}")
        
        return render(request, 'mascotas/atencion_detalle.html', {
            'atencion': atencion,
            'documentos_adjuntos': documentos_adjuntos,
        })
        
    except AtencionClinica.DoesNotExist:
        logger.error(f"Atención con ID {atencion_id} no encontrada")
        return render(request, 'mascotas/atencion_detalle.html', {
            'error': 'La atención médica especificada no fue encontrada.',
        })
    except Exception as e:
        logger.error(f"Error al cargar detalle de atención {atencion_id}: {e}")
        return render(request, 'mascotas/atencion_detalle.html', {
            'error': 'Ocurrió un error al cargar los detalles de la atención médica.',
        })


def ver_consentimiento(request, mascota_id):
    """
    Vista para ver información del consentimiento de una mascota.
    Retorna JSON con información del documento si existe.
    """
    try:
        mascota = Mascota.objects.get(id_mascota=mascota_id)
        
        # Verificar si existe documento de consentimiento
        if mascota.consentimiento and mascota.url_doc_consentimiento:
            # Extraer nombre del archivo de la URL
            nombre_archivo = mascota.url_doc_consentimiento.split('/')[-1]
            
            return JsonResponse({
                'success': True,
                'existe_documento': True,
                'documento': {
                    'id': mascota.id_mascota,  # Usar ID de mascota como identificador
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
        from datetime import datetime
        
        extension = archivo.name.split('.')[-1].lower()
        fecha = datetime.now().strftime('%Y%m%d')
        uuid_short = str(uuid.uuid4())[:8]
        nombre_archivo = f"consent_{mascota.nro_chip}_{fecha}_{uuid_short}.{extension}"
        
        # Guardar archivo en el sistema de archivos
        import os
        from django.conf import settings
        
        # Crear directorio si no existe
        directorio = os.path.join(settings.MEDIA_ROOT, 'consentimientos', str(mascota.id_mascota))
        os.makedirs(directorio, exist_ok=True)
        
        ruta_archivo = os.path.join(directorio, nombre_archivo)
        
        with open(ruta_archivo, 'wb+') as destino:
            for chunk in archivo.chunks():
                destino.write(chunk)
        
        # Actualizar consentimiento de la mascota
        url_relativa = f'consentimientos/{mascota.id_mascota}/{nombre_archivo}'
        
        mascota.consentimiento = True
        mascota.fecha_consentimiento = datetime.now().date()
        mascota.url_doc_consentimiento = url_relativa
        # Asignar clínica por defecto (ID = 1) - posteriormente se reemplazará por la clínica del usuario autenticado
        mascota.id_clinica_consentimiento_id = 1
        mascota.save()
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Documento de consentimiento subido exitosamente',
            'documento': {
                'id': mascota.id_mascota,  # Usar ID de mascota como identificador
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
        # Buscar la mascota por ID (documento_id es el id_mascota)
        mascota = Mascota.objects.get(id_mascota=documento_id)
        
        if not mascota.consentimiento or not mascota.url_doc_consentimiento:
            return JsonResponse({
                'success': False,
                'error': 'No existe documento de consentimiento para esta mascota'
            })
        
        # Construir ruta completa del archivo
        import os
        from django.conf import settings
        from django.http import FileResponse
        
        ruta_archivo = os.path.join(settings.MEDIA_ROOT, mascota.url_doc_consentimiento)
        
        if os.path.exists(ruta_archivo):
            # Extraer nombre del archivo de la URL
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
    Vista para mostrar PDFs de consentimiento en el navegador de manera segura.
    """
    try:
        # Buscar la mascota por ID (documento_id es el id_mascota)
        mascota = Mascota.objects.get(id_mascota=documento_id)
        
        if not mascota.consentimiento or not mascota.url_doc_consentimiento:
            return JsonResponse({
                'success': False,
                'error': 'No existe documento de consentimiento para esta mascota'
            })
        
        # Construir ruta completa del archivo
        import os
        from django.conf import settings
        from django.http import FileResponse
        
        ruta_archivo = os.path.join(settings.MEDIA_ROOT, mascota.url_doc_consentimiento)
        
        if os.path.exists(ruta_archivo):
            # Extraer extensión del archivo
            extension = os.path.splitext(mascota.url_doc_consentimiento)[1].lower()
            
            # Determinar el Content-Type apropiado
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
            response['Content-Disposition'] = 'inline'  # Mostrar en el navegador, no descargar
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
        logger.error(f"Error al ver consentimiento PDF: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Error al mostrar el documento'
        })