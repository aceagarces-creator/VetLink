from django.urls import path
from .views import buscar_tutor_view

urlpatterns = [
    path('buscar/', buscar_tutor_view, name='buscar_tutor'),
]