"""
URLs para la aplicación de mascotas.

Define las rutas URL para las vistas relacionadas con la gestión de mascotas.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('registrar/', views.registrar_mascota_view, name='registrar_mascota'),
    path('cargar-razas/', views.cargar_razas, name='cargar_razas'),
]