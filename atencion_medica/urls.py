"""
URLs para el módulo de atención médica.
"""

from django.urls import path
from . import views

app_name = 'atencion_medica'

urlpatterns = [
    # Buscar mascota para atención médica
    path('buscar-mascota/', views.buscar_mascota_atencion_view, name='buscar_mascota_atencion'),
    
    # Registrar atención médica
    path('registrar/<int:mascota_id>/', views.registrar_atencion_view, name='registrar_atencion'),
    
    # Listar atenciones
    path('listar/', views.listar_atenciones_view, name='listar_atenciones'),
    
    # Detalle de atención
    path('detalle/<int:atencion_id>/', views.detalle_atencion_view, name='detalle_atencion'),
    
    # AJAX - Cargar servicios detalle
    path('cargar-servicios-detalle/', views.cargar_servicios_detalle, name='cargar_servicios_detalle'),
]
