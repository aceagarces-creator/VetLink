from django.urls import path
from . import views

urlpatterns = [
    path('buscar/', views.buscar_tutor_view, name='buscar_tutor'),
    path('registrar/', views.registrar_tutor_view, name='registrar_tutor'),
    path('cargar-provincias/', views.cargar_provincias, name='cargar_provincias'),
    path('cargar-comunas/', views.cargar_comunas, name='cargar_comunas'),
    path('validar-rut/', views.validar_rut_tutor, name='validar_rut_tutor'),
]