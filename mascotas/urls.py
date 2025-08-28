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

    path('consentimiento/ver/<int:mascota_id>/', views.ver_consentimiento, name='ver_consentimiento'),
    path('consentimiento/subir/<int:mascota_id>/', views.subir_consentimiento, name='subir_consentimiento'),
    path('consentimiento/descargar/<int:documento_id>/', views.descargar_consentimiento, name='descargar_consentimiento'),
    path('consentimiento/ver-pdf/<int:documento_id>/', views.ver_consentimiento_pdf, name='ver_consentimiento_pdf'),
    path('atencion-detalle/<int:atencion_id>/', views.atencion_detalle_view, name='atencion_detalle'),
    path('documento-atencion/descargar/<int:documento_id>/', views.descargar_documento_atencion, name='descargar_documento_atencion'),
    path('documento-atencion/ver/<int:documento_id>/', views.ver_documento_atencion, name='ver_documento_atencion'),
    path('validar_mascota_duplicada/', views.validar_mascota_duplicada, name='validar_mascota_duplicada'),
]