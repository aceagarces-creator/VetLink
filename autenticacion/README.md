# Módulo de Autenticación VetLink

Este módulo proporciona un sistema de autenticación personalizado para la plataforma VetLink, que permite validar usuarios registrados en la base de datos y habilitar el acceso solo si están activos y asociados a una clínica.

## Características

- **Validación de credenciales**: Verifica email y contraseña contra la tabla USUARIO
- **Validación de cuenta activa**: Solo permite acceso a usuarios activos en clínicas activas
- **Protección reCAPTCHA**: Implementa Google reCAPTCHA para prevenir ataques automatizados
- **Gestión de sesiones**: Almacena información de usuario y clínica en variables de sesión
- **Mensajes de error seguros**: No expone información sensible en mensajes de error

## Estructura del Módulo

```
autenticacion/
├── __init__.py
├── apps.py
├── backends.py          # Backend de autenticación personalizado
├── decorators.py        # Decoradores para proteger vistas
├── forms.py            # Formulario de login con validación
├── urls.py             # Configuración de URLs
├── views.py            # Vistas de login, logout y dashboard
├── templates/
│   └── autenticacion/
│       ├── login.html      # Formulario de login
│       └── dashboard.html  # Dashboard post-login
└── README.md

Nota: Los modelos utilizados están en el directorio core/:
├── core/
│   ├── usuario_models.py
│   ├── personal_models.py
│   ├── clinicaVeterinaria_models.py
│   └── zona_geografica_models.py
```

## Componentes Principales

### 1. Backend de Autenticación (`backends.py`)

El `VetLinkAuthBackend` implementa la lógica de autenticación personalizada:

- Valida credenciales contra la tabla USUARIO (usando `core.usuario_models.Usuario`)
- Verifica que el usuario esté activo
- Confirma que el usuario esté asociado a una clínica activa (usando `core.personal_models.PersonalClinica` y `core.clinicaVeterinaria_models.ClinicaVeterinaria`)
- Almacena información de sesión (ID clínica, usuario, personal)

### 2. Formulario de Login (`forms.py`)

El `VetLinkLoginForm` extiende el formulario de autenticación de Django:

- Campos para email y contraseña
- Validación de reCAPTCHA
- Mensajes de error personalizados
- Validación de seguridad

### 3. Vistas (`views.py`)

- **LoginView**: Maneja el formulario de login
- **logout_view**: Cierra la sesión del usuario
- **dashboard_view**: Muestra el dashboard post-login

### 4. Decoradores (`decorators.py`)

- **@login_required**: Verifica que el usuario esté autenticado
- **@clinic_required**: Verifica que el usuario esté asociado a una clínica

## Configuración

### 1. Instalación

El módulo ya está incluido en `INSTALLED_APPS` en `settings.py`:

```python
INSTALLED_APPS = [
    # ... otras apps
    'autenticacion',
]
```

### 2. Backend de Autenticación

Configurado en `settings.py`:

```python
AUTHENTICATION_BACKENDS = [
    'autenticacion.backends.VetLinkAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]
```

### 3. reCAPTCHA

Configurado en `settings.py`:

```python
RECAPTCHA_SITE_KEY = 'tu_clave_publica'
RECAPTCHA_SECRET_KEY = 'tu_clave_secreta'
```

### 4. URLs

Incluidas en `vetlink_project/urls.py`:

```python
urlpatterns = [
    # ... otras URLs
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('dashboard/', auth_views.dashboard_view, name='dashboard'),
    path('autenticacion/', include('autenticacion.urls')),
]
```

## Uso

### 1. Acceso al Login

Navegar a `/login/` para acceder al formulario de autenticación.

### 2. Proteger Vistas

Usar los decoradores para proteger vistas que requieren autenticación:

```python
from autenticacion.decorators import login_required, clinic_required

@login_required
def mi_vista_protegida(request):
    # Solo usuarios autenticados pueden acceder
    pass

@clinic_required
def mi_vista_clinica(request):
    # Solo usuarios asociados a clínicas pueden acceder
    pass
```

### 3. Información de Sesión

Acceder a la información de sesión del usuario:

```python
# En cualquier vista
id_clinica = request.session.get('id_clinica')
id_usuario = request.session.get('id_usuario')
id_personal = request.session.get('id_personal')
email_usuario = request.session.get('email_usuario')
rol_usuario = request.session.get('rol_usuario')
```

## Seguridad

- **Contraseñas**: Se validan usando `check_password()` de Django
- **Sesiones**: Configuradas para expirar automáticamente
- **reCAPTCHA**: Previene ataques automatizados
- **Mensajes de error**: No exponen información sensible
- **CSRF**: Protección habilitada en todos los formularios

## Flujo de Autenticación

1. Usuario accede a `/login/`
2. Completa el formulario con email, contraseña y reCAPTCHA
3. Sistema valida credenciales contra la base de datos
4. Verifica que el usuario esté activo
5. Confirma asociación con clínica activa
6. Almacena información en sesión
7. Redirige al dashboard

## Mensajes de Error

- "Correo electrónico o contraseña incorrectos"
- "Su cuenta no está activa. Contacte al administrador"
- "Usuario no asociado a ninguna clínica"
- "Clínica no encontrada"
- "Por favor complete el reCAPTCHA"
- "Verificación reCAPTCHA fallida"

## Notas de Desarrollo

- Las claves de reCAPTCHA en `settings.py` son de prueba
- Para producción, reemplazar con claves reales de Google reCAPTCHA
- El módulo es completamente independiente y no afecta otras funcionalidades
- Compatible con la estructura de base de datos existente
- **Utiliza los modelos existentes del directorio `core/`** para evitar duplicación
- Los modelos utilizados son:
  - `core.usuario_models.Usuario`
  - `core.personal_models.PersonalClinica`
  - `core.clinicaVeterinaria_models.ClinicaVeterinaria`
  - `core.zona_geografica_models.Comuna` (para relaciones geográficas)
