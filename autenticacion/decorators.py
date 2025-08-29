from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def login_required(view_func):
    """
    Decorador para verificar que el usuario esté autenticado
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('id_usuario'):
            messages.error(request, 'Debe iniciar sesión para acceder a esta página.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def clinic_required(view_func):
    """
    Decorador para verificar que el usuario esté asociado a una clínica
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('id_clinica'):
            messages.error(request, 'Su cuenta no está asociada a ninguna clínica.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
