from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from core.usuario_models import Usuario
from core.personal_models import PersonalClinica
from core.clinicaVeterinaria_models import ClinicaVeterinaria
import bcrypt


class VetLinkAuthBackend(BaseBackend):
    """
    Backend de autenticación personalizado para VetLink
    Valida usuarios contra la tabla USUARIO y verifica que estén activos en una clínica
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Autenticar usuario usando email y contraseña
        """
        print("=== DEBUG BACKEND: Iniciando autenticación ===")
        print(f"Username: {username}")
        print(f"Password: {'*' * len(password) if password else 'None'}")
        
        if username is None or password is None:
            print("=== DEBUG BACKEND: Username o password son None ===")
            return None
        
        try:
            # Buscar usuario por email
            print(f"=== DEBUG BACKEND: Buscando usuario con email: {username} ===")
            usuario = Usuario.objects.get(email=username)
            print(f"=== DEBUG BACKEND: Usuario encontrado: {usuario.id_usuario} ===")
            
            # Verificar que el usuario esté activo
            print(f"=== DEBUG BACKEND: Usuario activo: {usuario.activo} ===")
            if not usuario.activo:
                raise ValidationError('Su cuenta no está activa. Contacte al administrador.')
            
            # Verificar contraseña con bcrypt
            print("=== DEBUG BACKEND: Verificando contraseña con bcrypt ===")
            print(f"=== DEBUG BACKEND: Hash almacenado: {usuario.password_hash} ===")
            
            try:
                # Convertir la contraseña a bytes y verificar con bcrypt
                password_bytes = password.encode('utf-8')
                hash_bytes = usuario.password_hash.encode('utf-8')
                password_valid = bcrypt.checkpw(password_bytes, hash_bytes)
                print(f"=== DEBUG BACKEND: Contraseña válida: {password_valid} ===")
                
                if not password_valid:
                    print("=== DEBUG BACKEND: Contraseña incorrecta ===")
                    return None
                    
            except Exception as e:
                print(f"=== DEBUG BACKEND: Error al verificar contraseña: {str(e)} ===")
                return None
            
            # Verificar que el usuario esté asociado a una clínica activa
            try:
                print(f"=== DEBUG BACKEND: Buscando personal_clinica para id_personal: {usuario.id_personal.id_personal} ===")
                personal_clinica = PersonalClinica.objects.get(id_personal=usuario.id_personal.id_personal)
                print(f"=== DEBUG BACKEND: Personal_clinica encontrado: {personal_clinica.id_clinica.id_clinica} ===")
                
                # Verificar que la clínica esté activa (asumiendo que hay un campo activo en ClinicaVeterinaria)
                # Si no existe el campo activo, se puede omitir esta validación
                clinica = ClinicaVeterinaria.objects.get(id_clinica=personal_clinica.id_clinica.id_clinica)
                print(f"=== DEBUG BACKEND: Clínica encontrada: {clinica.id_clinica} ===")
                
                # Almacenar información en la sesión
                if request:
                    print("=== DEBUG BACKEND: Almacenando datos en sesión ===")
                    
                    # Datos básicos del usuario
                    request.session['id_clinica'] = clinica.id_clinica
                    request.session['id_usuario'] = usuario.id_usuario
                    request.session['id_personal'] = usuario.id_personal.id_personal
                    request.session['email_usuario'] = usuario.email
                    request.session['rol_usuario'] = usuario.rol
                    
                    # Datos del personal
                    personal = usuario.id_personal
                    nombre_completo = f"{personal.nombres} {personal.apellido_paterno} {personal.apellido_materno}"
                    request.session['nombre_personal'] = nombre_completo
                    request.session['sexo_personal'] = personal.genero
                    request.session['profesion_personal'] = personal.profesion
                    
                    # Datos de la clínica
                    request.session['nombre_clinica'] = clinica.nombre
                    request.session['email_clinica'] = clinica.email
                    request.session['telefono_clinica'] = clinica.telefono
                    request.session['celular_clinica'] = clinica.celular
                    request.session['sitio_web_clinica'] = clinica.sitio_web
                    request.session['url_logo_clinica'] = clinica.url_logo
                    
                    print(f"=== DEBUG BACKEND: Sesión actualizada con datos completos ===")
                    print(f"=== DEBUG BACKEND: Personal: {nombre_completo} - Género: {personal.genero} ===")
                    print(f"=== DEBUG BACKEND: Clínica: {clinica.nombre} - Email: {clinica.email} ===")
                
                print("=== DEBUG BACKEND: Autenticación exitosa ===")
                return usuario
                
            except PersonalClinica.DoesNotExist:
                print("=== DEBUG BACKEND: PersonalClinica.DoesNotExist ===")
                raise ValidationError('Usuario no asociado a ninguna clínica.')
            except ClinicaVeterinaria.DoesNotExist:
                print("=== DEBUG BACKEND: ClinicaVeterinaria.DoesNotExist ===")
                raise ValidationError('Clínica no encontrada.')
                
        except Usuario.DoesNotExist:
            print("=== DEBUG BACKEND: Usuario.DoesNotExist ===")
            return None
        except ValidationError as e:
            print(f"=== DEBUG BACKEND: ValidationError: {str(e)} ===")
            # Re-raise ValidationError para que se maneje en la vista
            raise e
        except Exception as e:
            # Log del error para debugging (sin exponer detalles sensibles)
            print(f"=== DEBUG BACKEND: Exception: {str(e)} ===")
            import traceback
            traceback.print_exc()
            return None
    
    def get_user(self, user_id):
        """
        Obtener usuario por ID
        """
        try:
            return Usuario.objects.get(id_usuario=user_id)
        except Usuario.DoesNotExist:
            return None
