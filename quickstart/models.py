from django.db import models
from django.contrib.auth.models import User

class Carrera(models.Model):
    nombre = models.CharField(max_length=100)
    clave = models.CharField(max_length=10, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Materia(models.Model):
    nombre = models.CharField(max_length=100)
    clave = models.CharField(max_length=10, unique=True)
    creditos = models.IntegerField()
    carrera = models.ForeignKey(
        Carrera,
        on_delete=models.CASCADE,
        related_name='materias'
    )

    def __str__(self):
        return self.nombre


class Alumno(models.Model):
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100, blank=True)
    apellido_materno = models.CharField(max_length=100, blank=True)
    numero_control = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    carrera = models.ForeignKey(
        Carrera,
        on_delete=models.SET_NULL,   # ✅ corregido
        null=True,
        related_name='alumnos'
    )

    def __str__(self):
        return f'{self.nombre} {self.apellido_paterno} {self.apellido_materno}'


class Inscripcion(models.Model):
    alumno = models.ForeignKey(
        Alumno,
        on_delete=models.CASCADE,
        related_name='inscripciones'
    )
    materia = models.ForeignKey(
        Materia,
        on_delete=models.CASCADE,
        related_name='inscripciones'
    )
    fecha_inscripcion = models.DateField(auto_now_add=True)
    calificacion = models.DecimalField(   # ✅ corregido
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    ciclo = models.CharField(max_length=11, null=True, blank=True)

    class Meta:
        unique_together = ('alumno', 'materia')

    def __str__(self):
        return f'{self.alumno} - {self.materia}'

class Publicacion(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='publicaciones/', blank=True, null=True)

    def __str__(self):
        return self.titulo