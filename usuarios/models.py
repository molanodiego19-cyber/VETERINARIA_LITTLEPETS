from django.db import models
from datetime import time


class Usuario(models.Model):

    class Rol(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        VETERINARIO = 'veterinario', 'Veterinario'
        PROPIETARIO = 'propietario', 'Propietario'

    class Estado(models.TextChoices):
        ACTIVO = 'activo', 'Activo'
        INACTIVO = 'inactivo', 'Inactivo'
        SUSPENDIDO = 'suspendido', 'Suspendido'

    correo = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    fecha_cambio_password = models.DateTimeField(null=True, blank=True)
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.PROPIETARIO)
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.ACTIVO)
    last_login = models.DateTimeField(null=True,blank=True)
    intentos_fallidos = models.IntegerField(default=0)
    bloqueado_hasta = models.DateTimeField(null=True, blank=True)
    fecha_suspension = models.DateTimeField(null=True, blank=True)
    motivo_suspension = models.CharField(max_length=255, blank=True, null=True)
    
    def get_email_field_name(self):
        return 'correo'

    def es_veterinario(self):
        return self.rol == self.Rol.VETERINARIO
    
    def es_propietario(self):
        return self.rol == self.Rol.PROPIETARIO

    def es_admin(self):
        return self.rol == self.Rol.ADMIN

    def __str__(self):
        return self.correo
    

class Persona(models.Model):

    TIPO_DOCUMENTO_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('CE', 'Cédula de Extranjería'),
        ('TI', 'Tarjeta de Identidad'),
    ]
    nombre = models.CharField(max_length=60)
    apellido = models.CharField(max_length=50)
    telefono = models.CharField(max_length=10, blank=True, null=True)
    tipo_documento = models.CharField(max_length=20, choices=TIPO_DOCUMENTO_CHOICES)
    documento = models.CharField(max_length=10, unique=True)
    foto = models.ImageField(upload_to='perfiles/', blank=True, null=True, default='perfiles/default.svg')

    class Meta:
        abstract = True


class Administrador(Persona):

    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f"Admin: {self.nombre}"
    

class Propietario(Persona):

    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='propietario')
    ciudad = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.documento}"


class Veterinario(Persona):

    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='veterinario')
    especialidad = models.ForeignKey('veterinarioapp.Especialidad', on_delete=models.CASCADE)
    servicios = models.ManyToManyField('citas.Servicio', related_name='veterinarios', blank=True)
    num_licencia = models.CharField(max_length=50, unique=True)
    disponible = models.BooleanField(default=True)
    horario_inicio = models.TimeField(default=time(8, 0))
    horario_fin = models.TimeField(default=time(18, 0))
    dias_laborales = models.JSONField(default=list)
    fecha_creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.especialidad}"