from django.urls import path
from . import views

urlpatterns = [
    path('buscar-tutor/', views.buscar_tutor, name='buscar_tutor'),
]
