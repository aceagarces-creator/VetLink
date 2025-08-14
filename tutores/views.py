from django.shortcuts import render, redirect
from core.models import Tutor, Mascota, Nacionalidad, TutorNacionalidad
from .forms import BuscarTutorForm, RegistrarTutorForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from datetime import datetime

# Configurar logger
logger = logging.getLogger(__name__)

def buscar_tutor_view(request):
    tutor = None
    mascotas = []
    mensaje = None
    form = BuscarTutorForm()
    
    # Verificar si hay parámetro nro_documento en GET (viene desde el modal)
    nro_documento_get = request.GET.get('nro_documento')
    
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
            pass
    elif nro_documento_get:
        # Búsqueda automática desde el modal de RUT duplicado
        try:
            tutor = Tutor.objects.get(nro_documento=nro_documento_get)
            mascotas = Mascota.objects.filter(id_tutor=tutor)
            # Crear formulario precargado con el RUT
            form = BuscarTutorForm(initial={'nro_documento': nro_documento_get})
        except Tutor.DoesNotExist:
            mensaje = "Tutor no registrado en el sistema"
            form = BuscarTutorForm(initial={'nro_documento': nro_documento_get})
    
    return render(request, 'tutores/buscar_tutor.html', {
        'form': form,
        'tutor': tutor,
        'mascotas': mascotas,
        'mensaje': mensaje,
    })

def registrar_tutor_view(request):
    tutor_guardado = None
    modo_edicion = False
    mensaje_exito = None
    
    # Log para depuración
    logger.info(f"Método de request: {request.method}")
    
    if request.method == 'POST':
        logger.info("Procesando POST request")
        logger.info(f"Datos POST: {request.POST}")
        
        # Verificar si es modo edición (existe un tutor guardado)
        tutor_id = request.POST.get('tutor_id')
        if tutor_id:
            try:
                tutor_existente = Tutor.objects.get(id_tutor=tutor_id)
                modo_edicion = True
                logger.info(f"Modo edición activado para tutor: {tutor_existente}")
            except Tutor.DoesNotExist:
                logger.error(f"Tutor con ID {tutor_id} no encontrado")
                tutor_id = None
        
        # Crear el formulario con los datos POST y tutor_id si es modo edición
        if modo_edicion:
            form = RegistrarTutorForm(request.POST, tutor_id=tutor_id)
        else:
            form = RegistrarTutorForm(request.POST)
        
        # Configurar los querysets de provincia y comuna ANTES de validar
        if 'region' in request.POST and request.POST['region']:
            from core.models import Provincia
            region_id = request.POST['region']
            form.fields['provincia'].queryset = Provincia.objects.filter(id_region=region_id)
            
            if 'provincia' in request.POST and request.POST['provincia']:
                from core.models import Comuna
                provincia_id = request.POST['provincia']
                form.fields['comuna'].queryset = Comuna.objects.filter(id_provincia=provincia_id)
        
        logger.info(f"Formulario creado con querysets configurados")
        
        # Log de validación
        is_valid = form.is_valid()
        logger.info(f"Formulario válido: {is_valid}")
        
        if is_valid:
            if modo_edicion:
                logger.info("Actualizando tutor existente")
                try:
                    # Actualizar el tutor existente
                    tutor_existente.nombres = form.cleaned_data['nombres']
                    tutor_existente.apellido_paterno = form.cleaned_data['apellido_paterno']
                    tutor_existente.apellido_materno = form.cleaned_data['apellido_materno'] or ''
                    tutor_existente.email = form.cleaned_data['email']
                    tutor_existente.celular = form.cleaned_data['celular']
                    tutor_existente.telefono = form.cleaned_data['telefono'] or ''
                    tutor_existente.fecha_nacimiento = form.cleaned_data['fecha_nacimiento']
                    tutor_existente.calle = form.cleaned_data['calle']
                    tutor_existente.numero = form.cleaned_data['numero']
                    tutor_existente.departamento = request.POST.get('depto', '')  # Campo departamento del formulario
                    tutor_existente.codigo_postal = form.cleaned_data['codigo_postal'] or ''
                    tutor_existente.complemento = form.cleaned_data['complemento'] or ''
                    tutor_existente.id_comuna = form.cleaned_data['comuna']
                    # Actualizar fecha de última actualización
                    tutor_existente.fecha_ultima_actualizacion = datetime.now()
                    tutor_existente.save()
                    
                    logger.info(f"Tutor actualizado exitosamente: {tutor_existente}")
                    tutor_guardado = tutor_existente
                    
                except Exception as e:
                    logger.error(f"Error al actualizar tutor: {e}")
                    form.add_error(None, f"Error al actualizar el tutor: {str(e)}")
            else:
                logger.info("Formulario es válido, procediendo a crear tutor")
                logger.info(f"Datos limpios: {form.cleaned_data}")
                
                try:
                    # Crear el nuevo tutor
                    tutor = Tutor.objects.create(
                        tipo_documento='RUN',  # Valor por defecto
                        nro_documento=form.cleaned_data['nro_documento'],
                        nombres=form.cleaned_data['nombres'],
                        apellido_paterno=form.cleaned_data['apellido_paterno'],
                        apellido_materno=form.cleaned_data['apellido_materno'] or '',
                        email=form.cleaned_data['email'],
                        celular=form.cleaned_data['celular'],
                        telefono=form.cleaned_data['telefono'] or '',
                        fecha_nacimiento=form.cleaned_data['fecha_nacimiento'],
                        calle=form.cleaned_data['calle'],
                        numero=form.cleaned_data['numero'],
                        departamento=request.POST.get('depto', ''),  # Campo departamento del formulario
                        codigo_postal=form.cleaned_data['codigo_postal'] or '',
                        complemento=form.cleaned_data['complemento'] or '',
                        foto='',  # Campo vacío por defecto
                        id_comuna=form.cleaned_data['comuna'],
                        fecha_registro=datetime.now()  # Fecha de registro al crear
                    )
                    
                    logger.info(f"Tutor creado exitosamente: {tutor}")
                    
                    # Manejar nacionalidades
                    nacionalidad_principal = request.POST.get('nacionalidad')
                    nacionalidad_secundaria = request.POST.get('segunda_nacionalidad')
                    
                    # Guardar nacionalidad principal si existe
                    if nacionalidad_principal:
                        try:
                            nacionalidad_obj = Nacionalidad.objects.get(id_nacionalidad=nacionalidad_principal)
                            TutorNacionalidad.objects.create(
                                id_tutor=tutor,
                                id_nacionalidad=nacionalidad_obj,
                                fecha_registro=datetime.now()
                            )
                            logger.info(f"Nacionalidad principal guardada: {nacionalidad_obj.nacionalidad}")
                        except Nacionalidad.DoesNotExist:
                            logger.error(f"Nacionalidad con ID {nacionalidad_principal} no encontrada")
                    
                    # Guardar nacionalidad secundaria si existe
                    if nacionalidad_secundaria:
                        try:
                            nacionalidad_obj = Nacionalidad.objects.get(id_nacionalidad=nacionalidad_secundaria)
                            TutorNacionalidad.objects.create(
                                id_tutor=tutor,
                                id_nacionalidad=nacionalidad_obj,
                                fecha_registro=datetime.now()
                            )
                            logger.info(f"Nacionalidad secundaria guardada: {nacionalidad_obj.nacionalidad}")
                        except Nacionalidad.DoesNotExist:
                            logger.error(f"Nacionalidad con ID {nacionalidad_secundaria} no encontrada")
                    
                    tutor_guardado = tutor
                    mensaje_exito = f"El tutor '{tutor.nombres} {tutor.apellido_paterno}' ha sido registrado exitosamente"
                    
                except Exception as e:
                    logger.error(f"Error al crear tutor: {e}")
                    form.add_error(None, f"Error al guardar el tutor: {str(e)}")
            
            # Si el tutor se guardó exitosamente (creado o actualizado), precargar el formulario
            if tutor_guardado:
                # Crear un formulario precargado con los datos del tutor
                form_data = {
                    'nro_documento': tutor_guardado.nro_documento,
                    'nombres': tutor_guardado.nombres,
                    'apellido_paterno': tutor_guardado.apellido_paterno,
                    'apellido_materno': tutor_guardado.apellido_materno,
                    'email': tutor_guardado.email,
                    'celular': tutor_guardado.celular,
                    'telefono': tutor_guardado.telefono,
                    'fecha_nacimiento': tutor_guardado.fecha_nacimiento,
                    'nacionalidad': None,  # Por ahora no se maneja la nacionalidad
                    'region': tutor_guardado.id_comuna.id_provincia.id_region,
                    'provincia': tutor_guardado.id_comuna.id_provincia,
                    'comuna': tutor_guardado.id_comuna,
                    'calle': tutor_guardado.calle,
                    'numero': tutor_guardado.numero,
                    'depto': tutor_guardado.departamento,
                    'complemento': tutor_guardado.complemento,
                    'codigo_postal': tutor_guardado.codigo_postal,
                }
                
                # Crear formulario precargado con los datos del tutor
                form = RegistrarTutorForm(initial=form_data, tutor_id=tutor_guardado.id_tutor)
                
                # Configurar los querysets para que se muestren las opciones correctas
                from core.models import Provincia, Comuna
                form.fields['provincia'].queryset = Provincia.objects.filter(id_region=tutor_guardado.id_comuna.id_provincia.id_region.id_region)
                form.fields['comuna'].queryset = Comuna.objects.filter(id_provincia=tutor_guardado.id_comuna.id_provincia.id_provincia)
                
        else:
            logger.info("Formulario no es válido")
            logger.info(f"Errores del formulario: {form.errors}")
            
            # Mantener los querysets configurados para que se muestren las opciones correctas
            if 'region' in request.POST and request.POST['region']:
                from core.models import Provincia
                region_id = request.POST['region']
                form.fields['provincia'].queryset = Provincia.objects.filter(id_region=region_id)
                
                if 'provincia' in request.POST and request.POST['provincia']:
                    from core.models import Comuna
                    provincia_id = request.POST['provincia']
                    form.fields['comuna'].queryset = Comuna.objects.filter(id_provincia=provincia_id)
    else:
        logger.info("Request GET, creando formulario vacío")
        form = RegistrarTutorForm()
    
    logger.info(f"Tutor guardado: {tutor_guardado}")
    
    # Obtener todas las nacionalidades para el dropdown de segunda nacionalidad
    nacionalidades = Nacionalidad.objects.all()
    
    return render(request, 'tutores/registrar_tutor.html', {
        'form': form,
        'tutor_guardado': tutor_guardado,
        'modo_edicion': modo_edicion,
        'mensaje_exito': mensaje_exito,
        'nacionalidades': nacionalidades
    })

@csrf_exempt
def cargar_provincias(request):
    """Vista AJAX para cargar provincias según la región seleccionada"""
    if request.method == 'POST':
        data = json.loads(request.body)
        region_id = data.get('region_id')
        
        if region_id:
            from core.models import Provincia
            provincias = Provincia.objects.filter(id_region=region_id).values('id_provincia', 'provincia')
            return JsonResponse({'provincias': list(provincias)})
    
    return JsonResponse({'provincias': []})

@csrf_exempt
def validar_rut_tutor(request):
    """
    Vista AJAX para validar si un RUT ya existe en el sistema.
    """
    logger.info(f"Validación RUT - Método: {request.method}")  # Debug
    if request.method == 'POST':
        try:
            logger.info(f"Validación RUT - Body: {request.body}")  # Debug
            data = json.loads(request.body)
            rut = data.get('rut', '').strip()
            logger.info(f"Validación RUT - RUT recibido: {rut}")  # Debug
            
            if not rut:
                return JsonResponse({
                    'success': False,
                    'error': 'El RUT es obligatorio'
                })
            
            # Verificar si el RUT ya existe
            tutor_existe = Tutor.objects.filter(nro_documento=rut).exists()
            
            if tutor_existe:
                # Obtener información del tutor existente
                tutor_existente = Tutor.objects.get(nro_documento=rut)
                return JsonResponse({
                    'success': False,
                    'rut_existe': True,
                    'rut': rut,
                    'mensaje': f'El RUT {rut} ya está registrado para {tutor_existente.nombres} {tutor_existente.apellido_paterno}.',
                    'tutor_info': {
                        'nombres': tutor_existente.nombres,
                        'apellido_paterno': tutor_existente.apellido_paterno,
                        'apellido_materno': tutor_existente.apellido_materno or '',
                        'email': tutor_existente.email or '',
                        'celular': tutor_existente.celular or ''
                    }
                })
            else:
                return JsonResponse({
                    'success': True,
                    'rut_existe': False,
                    'mensaje': 'El RUT está disponible para registro'
                })
                
        except Exception as e:
            logger.error(f"Error al validar RUT: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Error al validar el RUT'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    })


@csrf_exempt
def cargar_comunas(request):
    """Vista AJAX para cargar comunas según la provincia seleccionada"""
    if request.method == 'POST':
        data = json.loads(request.body)
        provincia_id = data.get('provincia_id')
        
        if provincia_id:
            from core.models import Comuna
            comunas = Comuna.objects.filter(id_provincia=provincia_id).values('id_comuna', 'comuna')
            return JsonResponse({'comunas': list(comunas)})
    
    return JsonResponse({'comunas': []})
