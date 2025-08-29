from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
from .forms import VetLinkLoginForm
from .backends import VetLinkAuthBackend


@method_decorator(csrf_protect, name='dispatch')
class LoginView(View):
    """
    Vista para el formulario de login
    """
    template_name = 'autenticacion/login.html'
    form_class = VetLinkLoginForm
    
    def get(self, request):
        """
        Mostrar formulario de login
        """
        # Si el usuario ya está autenticado, redirigir al dashboard
        if request.session.get('id_usuario'):
            return redirect('dashboard')
        
        form = self.form_class()
        return render(request, self.template_name, {
            'form': form,
            'recaptcha_site_key': settings.RECAPTCHA_SITE_KEY
        })
    
    def post(self, request):
        """
        Procesar formulario de login
        """
        print("=== DEBUG: Iniciando procesamiento POST ===")
        print(f"Datos POST recibidos: {request.POST}")
        print(f"Datos POST como dict: {dict(request.POST)}")
        
        form = self.form_class(request.POST)
        print(f"Formulario válido: {form.is_valid()}")
        print(f"Datos del formulario: {form.data}")
        print(f"Campos del formulario: {list(form.fields.keys())}")
        
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            recaptcha_response = form.cleaned_data.get('recaptcha_response')
            
            print(f"Email: {email}")
            print(f"Password: {'*' * len(password) if password else 'None'}")
            print(f"reCAPTCHA: {'Completado' if recaptcha_response else 'No completado'}")
            
            try:
                # Usar el backend personalizado para autenticación
                backend = VetLinkAuthBackend()
                print("=== DEBUG: Llamando a backend.authenticate ===")
                usuario = backend.authenticate(request, username=email, password=password)
                print(f"Usuario retornado: {usuario}")
                
                if usuario is not None:
                    print("=== DEBUG: Usuario autenticado exitosamente ===")
                    # Login exitoso - usar nuestro backend personalizado sin last_login
                    from django.contrib.auth.models import AnonymousUser
                    
                    # Establecer el usuario en la sesión manualmente para evitar el error de last_login
                    request.session['_auth_user_id'] = usuario.id_usuario
                    request.session['_auth_user_backend'] = 'autenticacion.backends.VetLinkAuthBackend'
                    
                    # Actualizar fecha de última sesión
                    from django.utils import timezone
                    usuario.fecha_ultima_sesion = timezone.now()
                    usuario.save()
                    
                    messages.success(request, f'Bienvenido, {usuario.id_personal.nombres}!')
                    print("=== DEBUG: Redirigiendo a página principal ===")
                    return redirect('/')
                else:
                    print("=== DEBUG: Usuario no autenticado ===")
                    messages.error(request, 'Correo electrónico o contraseña incorrectos.')
                    
            except ValidationError as e:
                print(f"=== DEBUG: ValidationError: {str(e)} ===")
                messages.error(request, str(e))
            except Exception as e:
                # Log del error para debugging
                print(f"=== DEBUG: Exception en login: {str(e)} ===")
                import traceback
                traceback.print_exc()
                messages.error(request, 'Error interno del sistema. Por favor intente nuevamente.')
        else:
            print("=== DEBUG: Formulario inválido ===")
            print(f"Errores del formulario: {form.errors}")
            print(f"Errores detallados por campo:")
            for field_name, errors in form.errors.items():
                print(f"  Campo '{field_name}': {errors}")
                for error in errors:
                    if field_name == '__all__':
                        messages.error(request, error)
                    else:
                        field_label = form.fields[field_name].label if field_name in form.fields else field_name
                        messages.error(request, f'{field_label}: {error}')
        
        print("=== DEBUG: Renderizando formulario con errores ===")
        return render(request, self.template_name, {
            'form': form,
            'recaptcha_site_key': settings.RECAPTCHA_SITE_KEY
        })


@require_http_methods(["GET", "POST"])
def logout_view(request):
    """
    Vista para cerrar sesión
    """
    # Limpiar todos los mensajes antes de cerrar sesión
    storage = messages.get_messages(request)
    storage.used = True  # Marcar todos los mensajes como usados
    
    # Limpiar sesión
    logout(request)
    request.session.flush()
    
    # Agregar mensaje de logout después de limpiar
    messages.success(request, 'Sesión cerrada exitosamente.')
    return redirect('login')


def dashboard_view(request):
    """
    Vista del dashboard después del login
    """
    # Verificar que el usuario esté autenticado
    if not request.session.get('id_usuario'):
        messages.error(request, 'Debe iniciar sesión para acceder al dashboard.')
        return redirect('login')
    
    # Obtener información de la sesión
    context = {
        'id_clinica': request.session.get('id_clinica'),
        'id_usuario': request.session.get('id_usuario'),
        'id_personal': request.session.get('id_personal'),
        'email_usuario': request.session.get('email_usuario'),
        'rol_usuario': request.session.get('rol_usuario'),
    }
    
    return render(request, 'autenticacion/dashboard.html', context)
