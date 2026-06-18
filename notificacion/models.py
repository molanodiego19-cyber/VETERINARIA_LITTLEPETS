# notificacion/models.py
from django.db import models
from django.utils import timezone


class PlantillaNotificacion(models.Model):

    CANALES = [
        ("email", "Email"),
        ("sms", "SMS"),
        ("whatsapp", "WhatsApp"),
        ("push", "Push Notification"),
    ]

    canal = models.CharField(max_length=30, choices=CANALES)
    nombre = models.CharField(max_length=150, unique=True)
    asunto_plantilla = models.CharField(max_length=255)
    cuerpo_plantilla = models.TextField()
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class Notificacion(models.Model):

    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("enviada", "Enviada"),
        ("leida", "Leída"),
        ("error", "Error"),
    ]

    usuario = models.ForeignKey(
        "usuarios.Usuario", on_delete=models.CASCADE, related_name="notificaciones"
    )
    plantilla = models.ForeignKey(
        PlantillaNotificacion, on_delete=models.CASCADE, related_name="notificaciones"
    )
    cita = models.ForeignKey(
        "citas.Cita",
        on_delete=models.CASCADE,
        related_name="notificaciones",
        null=True,
        blank=True,
    )
    canal = models.CharField(max_length=30, editable=False)
    asunto = models.CharField(max_length=255, blank=True)
    cuerpo_mensaje = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    fecha_envio = models.DateTimeField(blank=True, null=True)
    error_detalle = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} - {self.estado}"

    # 🔥 MARCAR COMO ENVIADA
    def marcar_enviada(self):
        self.estado = "enviada"
        self.fecha_envio = timezone.now()
        self.save()

    # 🔥 MARCAR ERROR
    def marcar_error(self, error):
        self.estado = "error"
        self.error_detalle = str(error)
        self.save()
