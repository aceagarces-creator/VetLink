"""
URLs para el módulo de atención médica.
"""

from django.urls import path
from . import views

app_name = 'atencion_medica'

urlpatterns = [
    # Vista unificada para registrar atención médica
    path('registrar/', views.registrar_atencion_unificada_view, name='registrar_atencion_unificada'),
    
    # Registrar atención médica (sin parámetros - para redirección después de guardar)
    path('registrar-atencion/', views.registrar_atencion_unificada_view, name='registrar_atencion'),
    
    # Buscar mascota para atención médica (mantener para compatibilidad)
    path('buscar-mascota/', views.buscar_mascota_atencion_view, name='buscar_mascota_atencion'),
    
    # Registrar atención médica (mantener para compatibilidad)
    path('registrar/<int:mascota_id>/', views.registrar_atencion_view, name='registrar_atencion_con_mascota'),
    

    
    # AJAX - Cargar servicios detalle
    path('cargar-servicios-detalle/', views.cargar_servicios_detalle, name='cargar_servicios_detalle'),
]
