from django.db import models

class Tutor(models.Model):
    rut = models.CharField(max_length=10, unique=True)
    nombres = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, blank=True)
    correo = models.EmailField()
    celular = models.CharField(max_length=15)

    def __str__(self):
        return f'{self.nombres} {self.apellido_paterno}'

class Mascota(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='mascotas')
    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=50)
    raza = models.CharField(max_length=100)
    chip = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.nombre
