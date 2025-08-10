"""
URLs para la aplicación de mascotas.

Define las rutas URL para las vistas relacionadas con la gestión de mascotas.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('registrar/', views.registrar_mascota_view, name='registrar_mascota'),
    path('cargar-razas/', views.cargar_razas, name='cargar_razas'),
    path('validar-chip/', views.validar_chip, name='validar_chip'),
    path('ficha-clinica/', views.ficha_clinica_view, name='ficha_clinica'),
    path('atencion-detalle/<int:atencion_id>/', views.atencion_detalle_view, name='atencion_detalle'),
]