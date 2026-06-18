from django import forms
from .models import Especie, Raza, Mascota
from django.core.exceptions import ValidationError
from datetime import date
import re


class MascotaForm(forms.ModelForm):

    class Meta:
        model = Mascota
        fields = [
            "nombre",
            "especie",
            "raza",
            "fecha_nacimiento",
            "sexo",
            "peso_kg",
            "foto",
            "esterilizacion",
            "color",
        ]
        widgets = {
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔥 Siempre empezar vacío
        self.fields["raza"].queryset = Raza.objects.none()

        especie_id = None

        # ✔ CASO 1: FORM POST (IMPORTANTE: CON PREFIX)
        if self.data.get("especie"):
            especie_id = self.data.get("especie")

        # ✔ CASO 2: INITIAL (GET o edición parcial)
        elif self.initial.get("especie"):
            especie_id = self.initial.get("especie")

        # ✔ CASO 3: EDICIÓN REAL
        elif self.instance.pk and self.instance.especie:
            especie_id = self.instance.especie.id

        # 🔥 Cargar razas filtradas correctamente
        if especie_id:
            try:
                self.fields["raza"].queryset = Raza.objects.filter(
                    tipo_especie_id=int(especie_id)
                )
            except (ValueError, TypeError):
                self.fields["raza"].queryset = Raza.objects.none()

    # ─────────────────────────────
    # 🔹 VALIDACIONES INDIVIDUALES
    # ─────────────────────────────

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")

        if not nombre:
            raise forms.ValidationError("El nombre es obligatorio")

        if len(nombre) < 3:
            raise forms.ValidationError("Debe tener mínimo 3 caracteres")

        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", nombre):
            raise forms.ValidationError("Solo se permiten letras")

        return nombre.upper()

    def clean_color(self):
        color = self.cleaned_data.get("color")

        if not color:
            raise forms.ValidationError("El color es obligatorio")

        if len(color) < 3:
            raise forms.ValidationError("Debe tener mínimo 3 caracteres")

        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", color):
            raise forms.ValidationError("Solo se permiten letras")

        return color

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get("fecha_nacimiento")

        if fecha and fecha > date.today():
            raise forms.ValidationError("No puede ser una fecha futura")

        return fecha

    def clean_peso_kg(self):
        peso = self.cleaned_data.get("peso_kg")

        if peso is None:
            raise forms.ValidationError("El peso es obligatorio")

        if peso <= 0:
            raise forms.ValidationError("Debe ser mayor a 0")

        if peso > 100:
            raise forms.ValidationError("Peso demasiado alto")

        # ✔ decimales obligatorios
        if peso.as_tuple().exponent == 0:
            raise forms.ValidationError("Debe incluir decimales (ej: 10.50)")

        return peso

    # ─────────────────────────────
    # 🔥 VALIDACIÓN CRUZADA (CORREGIDA)
    # ─────────────────────────────

    def clean(self):
        cleaned_data = super().clean()

        especie = cleaned_data.get("especie")
        raza = cleaned_data.get("raza")

        if especie and raza:
            if raza.tipo_especie_id != especie.id:
                self.add_error(
                    "raza",
                    "La raza no pertenece a la especie seleccionada"
                )

        return cleaned_data


class EspecieForm(forms.ModelForm):
    class Meta:
        model = Especie
        fields = ["nombre", "descripcion"]


class RazaForm(forms.ModelForm):
    class Meta:
        model = Raza
        fields = ["nombre", "tipo_especie"]
