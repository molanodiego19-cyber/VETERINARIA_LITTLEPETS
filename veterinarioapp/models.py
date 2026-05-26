from django.db import models
from django.core.exceptions import ValidationError

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class HorarioVeterinario(models.Model):
    DIAS = [
    (1,'Lunes'),
    (2,'Martes'),
    (3,'Miércoles'),
    (4,'Jueves'),
    (5,'Viernes'),
    (6,'Sábado'),
    (7,'Domingo'),
]

    veterinario = models.ForeignKey('usuarios.Veterinario', on_delete=models.CASCADE)
    dias_semana = models.IntegerField(choices=DIAS)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    intervalo_min = models.IntegerField()
    activo = models.BooleanField(default=True)
    fecha_desde = models.DateField()
    fecha_hasta = models.DateField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
     return f"{self.veterinario} - {self.get_dias_semana_display()}"

class BloqueoAgenda(models.Model):

    TIPO_BLOQUEO = [
        ('vacaciones', 'Vacaciones'),
        ('permiso', 'Permiso'),
        ('reunion', 'Reunión'),
        ('otro', 'Otro'),
    ]
    veterinario = models.ForeignKey('usuarios.Veterinario',on_delete=models.CASCADE,related_name="bloqueos")
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    motivo = models.CharField(max_length=150)
    tipo = models.CharField(max_length=20,choices=TIPO_BLOQUEO )
    todo_el_dia = models.BooleanField(default=True)
    recurrente = models.BooleanField(default=False)
    creado_por = models.ForeignKey('usuarios.Veterinario',on_delete=models.CASCADE,related_name="bloqueos_creados")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
  
    def clean(self):
        # 1. Validar rango de fechas
        if self.fecha_inicio >= self.fecha_fin:
            raise ValidationError("La fecha de inicio debe ser menor que la fecha fin")

        # 2. Validar solapamiento de bloqueos
        bloqueos = BloqueoAgenda.objects.filter(
            veterinario=self.veterinario,
            fecha_inicio__lt=self.fecha_fin,
            fecha_fin__gt=self.fecha_inicio
        )

        # Excluir el mismo objeto en edición
        if self.pk:
            bloqueos = bloqueos.exclude(pk=self.pk)

        if bloqueos.exists():
            raise ValidationError("Ya existe un bloqueo en ese rango de fechas para este veterinario")

    def __str__(self):
        return f"{self.veterinario} - {self.get_tipo_display()} ({self.fecha_inicio} - {self.fecha_fin})"
    