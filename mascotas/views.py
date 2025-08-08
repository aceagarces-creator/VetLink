"""
Vistas para la gestión de mascotas.

Este módulo contiene las vistas para la gestión de mascotas,
incluyendo registro de nuevas mascotas y búsqueda de tutores.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from core.models import Tutor, Mascota, Especie, Raza
from .forms import BuscarTutorMascotaForm, RegistrarMascotaForm
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