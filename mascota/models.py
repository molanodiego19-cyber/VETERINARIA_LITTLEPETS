from django.db import models

class Especie (models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100)

    def __str__(self):
     return f"{self.nombre}"

class Raza (models.Model):
    nombre = models.CharField(max_length=50)
    tipo_especie = models.ForeignKey(Especie, on_delete=models.CASCADE)

    def __str__(self):
     return f"{self.nombre}"

class Mascota(models.Model):

    TIPO_SEXO = [
        ('hembra', 'Hembra'),
        ('macho', 'Macho'),
    ]

    class Estado(models.TextChoices):
        ACTIVO = 'activo', 'Activo'
        INACTIVO = 'inactivo', 'Inactivo'

    propietario = models.ForeignKey('usuarios.Propietario', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50)
    especie = models.ForeignKey(Especie, on_delete=models.CASCADE)
    raza = models.ForeignKey (Raza, on_delete=models.CASCADE)
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=10, choices=TIPO_SEXO)
    peso_kg = models.DecimalField(max_digits=5, decimal_places=2)
    foto = models.ImageField(upload_to='mascotas/', blank=True, null=True)
    esterilizacion = models.BooleanField(default=False)
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.ACTIVO)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    color = models.CharField(max_length=20)

    def __str__(self):
     return f"{self.nombre} - {self.raza}"
    

