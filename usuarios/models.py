from django.db import models
from datetime import time
from django.core.exceptions import ValidationError
from django.utils import timezone
import re

class Usuario(models.Model):

    class Rol(models.TextChoices):
        ADMIN = "admin", "Administrador"
        VETERINARIO = "veterinario", "Veterinario"
        RECEPCIONISTA = "recepcionista", "Resepcionista"
        PROPIETARIO = "propietario", "Propietario"

    class Estado(models.TextChoices):
        ACTIVO = "activo", "Activo"
        INACTIVO = "inactivo", "Inactivo"
        SUSPENDIDO = "suspendido", "Suspendido"

    correo = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    fecha_cambio_password = models.DateTimeField(null=True, blank=True)
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.PROPIETARIO)
    estado = models.CharField(
        max_length=10, choices=Estado.choices, default=Estado.ACTIVO
    )
    last_login = models.DateTimeField(null=True, blank=True)
    intentos_fallidos = models.IntegerField(default=0)
    bloqueado_hasta = models.DateTimeField(null=True, blank=True)
    fecha_suspension = models.DateTimeField(null=True, blank=True)
    motivo_suspension = models.CharField(max_length=255, blank=True, null=True)

    def get_email_field_name(self):
        return "correo"

    def es_veterinario(self):
        return self.rol == self.Rol.VETERINARIO

    def es_propietario(self):
        return self.rol == self.Rol.PROPIETARIO

    def es_admin(self):
        return self.rol == self.Rol.ADMIN

    def __str__(self):
        return self.correo


import re
from django.db import models
from django.core.exceptions import ValidationError


class Persona(models.Model):

    TIPO_DOCUMENTO_CHOICES = [
        ("CC", "Cédula de Ciudadanía"),
        ("CE", "Cédula de Extranjería"),
        ("TI", "Tarjeta de Identidad"),
    ]

    nombre = models.CharField(max_length=60)
    apellido = models.CharField(max_length=50)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    tipo_documento = models.CharField(max_length=20, choices=TIPO_DOCUMENTO_CHOICES)
    documento = models.CharField(max_length=10, unique=True)

    foto = models.ImageField(
        upload_to="perfiles/",
        blank=True,
        null=True,
        default="perfiles/default.svg"
    )

    class Meta:
        abstract = True

    # =========================
    # 🔧 VALIDADORES
    # =========================

    @staticmethod
    def validar_texto(nombre_campo, valor):
        if not valor:
            raise ValidationError(f"{nombre_campo} es obligatorio")

        valor = valor.strip()

        if len(valor) < 2:
            raise ValidationError(f"{nombre_campo} muy corto")

        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", valor):
            raise ValidationError(f"{nombre_campo} solo puede contener letras")

        return valor.title()

    @staticmethod
    def validar_telefono(valor):
        if not valor:
            return valor

        valor = str(valor).strip()
        valor = re.sub(r"\s+", "", valor)

        if not re.match(r"^\+?\d{7,15}$", valor):
            raise ValidationError("Teléfono inválido")

        return valor

    @staticmethod
    def validar_documento(valor):
        if not valor:
            raise ValidationError("Documento es obligatorio")

        valor = str(valor).strip()

        if not re.match(r"^\d{6,10}$", valor):
            raise ValidationError("Documento debe tener entre 6 y 10 dígitos")

        return valor

    # =========================
    # 🔥 CLEAN CENTRAL
    # =========================
    def clean(self):
        errors = {}

        try:
            self.nombre = self.validar_texto("Nombre", self.nombre)
        except ValidationError as e:
            errors["nombre"] = str(e)

        try:
            self.apellido = self.validar_texto("Apellido", self.apellido)
        except ValidationError as e:
            errors["apellido"] = str(e)

        try:
            self.telefono = self.validar_telefono(self.telefono)
        except ValidationError as e:
            errors["telefono"] = str(e)

        try:
            self.documento = self.validar_documento(self.documento)
        except ValidationError as e:
            errors["documento"] = str(e)

        if errors:
            raise ValidationError(errors)


class Administrador(Persona):

    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f"Admin: {self.nombre}"


class Propietario(Persona):

    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name="propietario"
    )
    ciudad = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.documento}"


class Recepcionista(Persona):

    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name="recepcionista"
    )

    ciudad = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    fecha_contratacion = models.DateTimeField(auto_now_add=True)

    turno = models.CharField(
        max_length=50,
        choices=[
            ("mañana", "Mañana"),
            ("tarde", "Tarde"),
            ("nocturno", "Nocturno"),
        ],
        default="mañana",
    )

    activo = models.BooleanField(default=True)

    def clean(self):

        errors = {}

        # 🔹 nombre (viene de Persona)
        if hasattr(self, "nombre") and self.nombre:
            if len(self.nombre) < 3:
                errors["nombre"] = "El nombre debe tener mínimo 3 caracteres"

            if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", self.nombre):
                errors["nombre"] = "El nombre solo puede contener letras"

        else:
            errors["nombre"] = "El nombre es obligatorio"

        # 🔹 documento (Persona)
        if hasattr(self, "documento") and self.documento:
            if len(str(self.documento)) < 6:
                errors["documento"] = "El documento es demasiado corto"
        else:
            errors["documento"] = "El documento es obligatorio"

        # 🔹 ciudad
        if not self.ciudad:
            errors["ciudad"] = "La ciudad es obligatoria"

        elif len(self.ciudad) < 3:
            errors["ciudad"] = "La ciudad debe tener mínimo 3 caracteres"

        elif not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", self.ciudad):
            errors["ciudad"] = "La ciudad solo puede contener letras"

        # 🔹 dirección
        if not self.direccion:
            errors["direccion"] = "La dirección es obligatoria"

        elif len(self.direccion) < 5:
            errors["direccion"] = "La dirección es demasiado corta"

        # 🔹 fecha contratación
        if self.fecha_contratacion:
            if self.fecha_contratacion > timezone.now():
                errors["fecha_contratacion"] = "La fecha no puede ser futura"

        # 🔹 turno
        valid_turnos = ["mañana", "tarde", "nocturno"]

        if self.turno not in valid_turnos:
            errors["turno"] = "Debe seleccionar un turno válido"

        # 🔹 activo
        if self.activo not in [True, False]:
            errors["activo"] = "Estado inválido"

        # 🚨 lanzar errores
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.nombre} - Recepcionista ({self.documento})"


class Veterinario(Persona):

    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name="veterinario"
    )
    especialidad = models.ForeignKey(
        "veterinarioapp.Especialidad", on_delete=models.CASCADE
    )
    servicios = models.ManyToManyField(
        "citas.Servicio", related_name="veterinarios", blank=True
    )
    num_licencia = models.CharField(max_length=50, unique=True)
    disponible = models.BooleanField(default=True)
    horario_inicio = models.TimeField(default=time(8, 0))
    horario_fin = models.TimeField(default=time(18, 0))
    dias_laborales = models.JSONField(default=list)
    fecha_creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.especialidad}"
