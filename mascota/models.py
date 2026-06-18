from django.db import models
from django.utils import timezone
import re
from django.core.exceptions import ValidationError

class Especie(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre}"


class Raza(models.Model):
    nombre = models.CharField(max_length=50)
    tipo_especie = models.ForeignKey(Especie, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre}"


class Mascota(models.Model):

    TIPO_SEXO = [
        ("hembra", "Hembra"),
        ("macho", "Macho"),
    ]

    class Estado(models.TextChoices):
        ACTIVO = "activo", "Activo"
        INACTIVO = "inactivo", "Inactivo"

    propietario = models.ForeignKey("usuarios.Propietario", on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50)
    especie = models.ForeignKey(Especie, on_delete=models.CASCADE)
    raza = models.ForeignKey(Raza, on_delete=models.CASCADE)
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=10, choices=TIPO_SEXO)
    peso_kg = models.DecimalField(max_digits=5, decimal_places=2)
    foto = models.ImageField(upload_to="mascotas/", blank=True, null=True)
    esterilizacion = models.BooleanField(default=False)
    estado = models.CharField(
        max_length=10, choices=Estado.choices, default=Estado.ACTIVO
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    color = models.CharField(max_length=20)

    def clean(self):

        errors = {}

        # 🔹 nombre
        if not self.nombre:
            errors["nombre"] = "El nombre es obligatorio"

        if self.nombre and len(self.nombre) < 3:
            errors["nombre"] = "El nombre debe tener mínimo 3 caracteres"

        if self.nombre and not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", self.nombre):
            errors["nombre"] = "El nombre solo puede contener letras"

        # 🔹 peso
        if self.peso_kg is not None:
            if self.peso_kg <= 0:
                errors["peso_kg"] = "El peso debe ser mayor a 0"
            if self.peso_kg > 200:
                errors["peso_kg"] = "El peso no puede superar 200 kg"

        # 🔹 fecha nacimiento
        if self.fecha_nacimiento:
            if self.fecha_nacimiento > timezone.now().date():
                errors["fecha_nacimiento"] = "La fecha no puede ser futura"

        # 🔹 color
        if self.color:
            if len(self.color) < 3:
                errors["color"] = "El color debe tener mínimo 3 caracteres"
            if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", self.color):
                errors["color"] = "El color solo debe contener letras"

        # 🔹 especie y raza obligatorias
        if not self.especie:
            errors["especie"] = "Debe seleccionar una especie"

        if not self.raza:
            errors["raza"] = "Debe seleccionar una raza"

        # 🔹 sexo obligatorio
        if not self.sexo:
            errors["sexo"] = "Debe seleccionar el sexo"

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.nombre} - {self.raza}"
