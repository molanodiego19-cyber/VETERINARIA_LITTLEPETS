from django.db import models
from django.core.validators import (MinValueValidator,MaxValueValidator)
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.db.models import Q

# CLASE CITA
class Cita(models.Model):

    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('finalizada', 'Finalizada'),
        ('en_proceso', 'En Proceso'),
        ('no_asistio', 'No Asistio')
    ]

    dueño = models.ForeignKey('usuarios.Propietario', on_delete=models.CASCADE, related_name='citas')
    mascota = models.ForeignKey('mascota.Mascota', on_delete=models.CASCADE, related_name='citas')
    veterinario = models.ForeignKey('usuarios.Veterinario',on_delete=models.CASCADE, related_name='citas', null=True, blank=True)
    servicio = models.ForeignKey('citas.Servicio', on_delete=models.CASCADE, related_name='citas')
    fecha = models.DateField()
    hora = models.TimeField()
    motivo_consulta = models.CharField(max_length=200)
    notas_adicionales = models.TextField(max_length=200, blank=True, null=True)
    estado = models.CharField(max_length=15, choices=ESTADOS, default='pendiente')
    recordatorio_enviado = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=['fecha', 'hora', 'veterinario'],
                condition=Q(
                    estado__in=[
                        'pendiente',
                        'confirmada'
                    ]
                ),
                name='unique_cita_activa'
            )
        ]

    def clean(self):

        if self.fecha and self.fecha < datetime.now().date():

            raise ValidationError(
                "No puedes agendar en fechas pasadas"
            )

        if self.fecha and self.hora and self.servicio:

            inicio = datetime.combine(
                self.fecha,
                self.hora
            )

            fin = inicio + timedelta(
                minutes=self.servicio.duracion_minutos
            )

            # VALIDAR HORARIO VETERINARIO
            if self.veterinario:

                citas = Cita.objects.filter(
                    veterinario=self.veterinario,
                    fecha=self.fecha,
                    estado__in=[
                        'pendiente',
                        'confirmada',
                        'en_proceso'
                    ]
                ).exclude(pk=self.pk)

                for cita in citas:

                    cita_inicio = datetime.combine(
                        cita.fecha,
                        cita.hora
                    )

                    cita_fin = cita_inicio + timedelta(
                        minutes=cita.servicio.duracion_minutos
                    )

                    if inicio < cita_fin and fin > cita_inicio:

                        raise ValidationError(
                            "El veterinario ya tiene "
                            "una cita en ese horario"
                        )
                    
            # VALIDAR HORARIO MASCOTA
            if self.mascota:

                citas_mascota = Cita.objects.filter(
                    mascota=self.mascota,
                    fecha=self.fecha,
                    estado__in=[
                        'pendiente',
                        'confirmada',
                        'en_proceso'
                    ]
                ).exclude(pk=self.pk)

                for cita in citas_mascota:

                    cita_inicio = datetime.combine(
                        cita.fecha,
                        cita.hora
                    )

                    cita_fin = cita_inicio + timedelta(
                        minutes=cita.servicio.duracion_minutos
                    )

                    if inicio < cita_fin and fin > cita_inicio:

                        raise ValidationError(
                            f"La mascota ya tiene "
                            f"una cita entre "
                            f"{cita.hora} y "
                            f"{cita_fin.time()}"
                        )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"Cita {self.mascota} - "
            f"{self.fecha} - {self.hora}"
        )
    
# CLASE CONSULTA
# CLASE CONSULTA
class Consulta(models.Model):

    cita = models.ForeignKey(
        Cita,
        on_delete=models.CASCADE,
        related_name='consultas'
    )
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    anamnesis = models.TextField()
    examen_fisico = models.TextField()

    diagnostico_presuntivo = models.TextField()
    diagnostico_definitivo = models.TextField()

    plan_terapeutico = models.TextField()
    observaciones = models.TextField()

    peso_en_consulta = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    temperatura = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[
            MinValueValidator(35),
            MaxValueValidator(42)
        ],
        null=True,
        blank=True
    )

    frecuencia_cardiaca = models.IntegerField()
    frecuencia_respiratoria = models.IntegerField()

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def crear_historia_clinica(self):

        return HistoriaClinica.objects.create(

            tipo_registro='consulta',

            mascota=self.cita.mascota,
            veterinario=self.cita.veterinario,
            cita=self.cita,

            fecha_consulta=self.cita.fecha,

            peso_kg=self.peso_en_consulta,
            temperatura=self.temperatura,
            frecuencia_cardiaca=self.frecuencia_cardiaca,
            frecuencia_respiratoria=self.frecuencia_respiratoria,

            motivo_consulta=(
                f"{self.cita.servicio.nombre} - "
                f"{self.cita.motivo_consulta}"
            ),

            anamnesis=self.anamnesis,
            examen_fisico=self.examen_fisico,

            diagnostico=(
                self.diagnostico_definitivo
                or self.diagnostico_presuntivo
            ),

            tratamiento=self.plan_terapeutico,

            medicamentos_dosis="",

            recomendaciones=self.observaciones,
        )

    def __str__(self):

        return (
            f"Consulta de "
            f"{self.cita.mascota.nombre}"
        )
    
# CLASE HISTORIACLINICA
class HistoriaClinica(models.Model):

    TIPOS = [
        ('consulta', 'Consulta'),
        ('vacunacion', 'Vacunación'),
        ('servicio', 'Servicio'),
    ]

    tipo_registro = models.CharField(max_length=20, choices=TIPOS)

    mascota = models.ForeignKey(
        'mascota.Mascota',
        on_delete=models.CASCADE
    )

    veterinario = models.ForeignKey(
        'usuarios.Veterinario',
        on_delete=models.CASCADE
    )

    cita = models.ForeignKey(
        Cita,
        on_delete=models.CASCADE
    )

    fecha_consulta = models.DateField()

    peso_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    temperatura = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True
    )

    frecuencia_cardiaca = models.IntegerField(
        null=True,
        blank=True
    )

    frecuencia_respiratoria = models.IntegerField(
        null=True,
        blank=True
    )

    motivo_consulta = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    anamnesis = models.TextField(
        blank=True,
        null=True
    )

    examen_fisico = models.TextField(
        blank=True,
        null=True
    )

    diagnostico = models.TextField(
        blank=True,
        null=True
    )

    tratamiento = models.TextField(
        blank=True,
        null=True
    )

    medicamentos_dosis = models.TextField(
        blank=True,
        null=True
    )

    recomendaciones = models.TextField(
        blank=True,
        null=True
    )

    notas = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return (
            f"{self.get_tipo_registro_display()} - "
            f"{self.mascota}"
        )
    
# CLASE CATEGORIASERVICIOS
class CategoriaServicios(models.Model):

    nombre_categoria = models.CharField(
        max_length=100
    )

    def __str__(self):

        return self.nombre_categoria

# CLASE SERVICIO
class Servicio(models.Model):

    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    duracion_minutos = models.IntegerField()
    categoria = models.ForeignKey(CategoriaServicios, on_delete=models.CASCADE)
    especialista_required = models.ForeignKey('veterinarioapp.Especialidad', on_delete=models.SET_NULL, null=True,        blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    
# CLASE MEDICAMENTO
class Medicamento(models.Model):

    nombre_comercial = models.CharField(max_length=150)
    principio_activo = models.CharField(max_length=150)
    presentacion = models.CharField(max_length=80)
    concentracion = models.CharField(max_length=80)
    via_administracion = models.CharField(max_length=80)
    horas_intervalo = models.IntegerField()
    fabricante = models.CharField(max_length=150)
    stock_actual = models.IntegerField()
    stock_minimo = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    servicio = models.ForeignKey('citas.Servicio', on_delete=models.SET_NULL, null=True, blank=True,        related_name='medicamentos')
    fecha_vencimiento = models.DateField()
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_comercial
    
# CLASE TRATAMIENTO
class Tratamiento(models.Model):

    ESTADO = [
        ('activo', 'Activo'),
        ('finalizado', 'Finalizado'),
        ('suspendido', 'Suspendido'),
    ]

    consulta = models.ForeignKey(Consulta, on_delete=models.CASCADE, related_name='tratamientos')
    veterinario = models.ForeignKey('usuarios.Veterinario', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    medicamento = models.CharField(max_length=200)
    dosis = models.DecimalField(max_digits=5,decimal_places=2,default=0)
    frecuencia = models.CharField(max_length=80)
    instrucciones = models.TextField()
    duracion_dias = models.IntegerField()
    estado = models.CharField(max_length=20, choices=ESTADO, default='activo')
    observaciones = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    
# CLASE HISTORIALSERVICIO
class HistorialServicio(models.Model):

    cita = models.ForeignKey(Cita, on_delete=models.CASCADE, related_name='historial_servicios')
    observaciones = models.TextField( blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.cita.mascota.nombre} - "
            f"{self.cita.servicio.nombre}"
        )

# CLASE VACUNA
class Vacuna(models.Model):

    nombre = models.CharField(max_length=50)
    fabricante = models.CharField(max_length=50)
    especie_objetivo = models.ForeignKey('mascota.Especie', on_delete=models.CASCADE)
    enfermedades = models.TextField()
    dosis_total = models.IntegerField()
    intervalo_dosis = models.IntegerField()
    refuerzo_meses = models.IntegerField()
    edad_minima_dias = models.IntegerField()
    requiere_frio = models.BooleanField()
    lote = models.CharField(max_length=80, blank=True, null=True)
    fecha_vencimiento = models.DateField(blank=True, null=True)
    activo = models.BooleanField()
    fecha_creacion = models.DateTimeField()

    def __str__(self):
        return (
            f"{self.nombre} - "
            f"{self.fabricante}"
        )
    
# CLASE VACUNACION
class Vacunacion(models.Model):

    cita = models.ForeignKey(
        Cita,
        on_delete=models.CASCADE,
        related_name='vacunaciones'
    )

    vacuna = models.ForeignKey(
        Vacuna,
        on_delete=models.CASCADE
    )

    fecha_aplicacion = models.DateField(auto_now_add=True)

    numero_dosis = models.IntegerField()

    fecha_proxima = models.DateField(
        blank=True,
        null=True
    )

    observaciones = models.TextField(
        blank=True,
        null=True
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    def crear_historia_clinica(self):

        return HistoriaClinica.objects.create(

            tipo_registro='vacunacion',

            mascota=self.cita.mascota,
            veterinario=self.cita.veterinario,
            cita=self.cita,

            fecha_consulta=self.fecha_aplicacion,

            motivo_consulta=f"Vacunación - {self.vacuna.nombre}",

            diagnostico=f"Aplicación de vacuna {self.vacuna.nombre}",

            medicamentos_dosis=f"Dosis #{self.numero_dosis}",

            recomendaciones=self.observaciones,

            notas=(
                f"Próxima dosis: {self.fecha_proxima}"
                if self.fecha_proxima else ""
            )
        )

    def __str__(self):

        return (
            f"{self.cita.mascota.nombre} - "
            f"{self.vacuna.nombre} "
            f"(Dosis {self.numero_dosis})"
        )