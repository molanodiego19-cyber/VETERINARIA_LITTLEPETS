from django import forms
from usuarios.models import Propietario, Veterinario
from mascota.models import Mascota
from django.contrib.auth.hashers import check_password, make_password
from datetime import date
import re
from mascota.models import Raza


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
        if self.data.get("mascota-especie"):
            especie_id = self.data.get("mascota-especie")

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


class PerfilVeterinarioForm(forms.ModelForm):

    dias_laborales = forms.MultipleChoiceField(
        choices=[
            ("lunes", "Lunes"),
            ("martes", "Martes"),
            ("miercoles", "Miércoles"),
            ("jueves", "Jueves"),
            ("viernes", "Viernes"),
            ("sabado", "Sábado"),
            ("domingo", "Domingo"),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    class Meta:
        model = Veterinario
        fields = [
            "nombre",
            "apellido",
            "telefono",
            "foto",
            "especialidad",
            "num_licencia",
            "disponible",
            "horario_inicio",
            "horario_fin",
            "dias_laborales",
        ]

        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "apellido": forms.TextInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "foto": forms.FileInput(attrs={"class": "form-control"}),
            "especialidad": forms.Select(attrs={"class": "form-control"}),
            "num_licencia": forms.TextInput(attrs={"class": "form-control"}),
            "disponible": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "horario_inicio": forms.TimeInput(
                attrs={"class": "form-control", "type": "time"}
            ),
            "horario_fin": forms.TimeInput(
                attrs={"class": "form-control", "type": "time"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields["dias_laborales"].initial = (
                self.instance.dias_laborales or []
            )

    # VALIDACIONES INDIVIDUALES

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")

        if not nombre:
            raise forms.ValidationError("El nombre es obligatorio")

        if len(nombre) < 3:
            raise forms.ValidationError("El nombre debe tener mínimo 3 caracteres")

        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", nombre):
            raise forms.ValidationError("El nombre solo puede contener letras")

        return nombre.upper()

    def clean_apellido(self):
        apellido = self.cleaned_data.get("apellido")

        if not apellido:
            raise forms.ValidationError("El apellido es obligatorio")

        if len(apellido) < 3:
            raise forms.ValidationError("Mínimo 3 caracteres")

        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", apellido):
            raise forms.ValidationError("Solo se permiten letras")

        return apellido.upper()

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono")

        if not telefono:
            raise forms.ValidationError("El teléfono es obligatorio")

        if not telefono.isdigit():
            raise forms.ValidationError("El teléfono solo debe contener números")

        if len(telefono) != 10:
            raise forms.ValidationError("El teléfono debe tener 10 dígitos")

        if (
            Propietario.objects.filter(telefono=telefono)
            .exclude(id=self.instance.id)
            .exists()
        ):
            raise forms.ValidationError("Este teléfono ya está registrado")

        return telefono

    def clean_num_licencia(self):
        licencia = self.cleaned_data.get("num_licencia")
        if len(licencia) < 5:
            raise forms.ValidationError("El número de licencia es demasiado corto.")
        return licencia

    def clean_dias_laborales(self):
        dias = self.cleaned_data.get("dias_laborales", [])

        if not dias:
            raise forms.ValidationError(
                "Debe seleccionar al menos un día"
            )

        return dias
    # VALIDACIÓN GENERAL (CRUZADA)

    def clean(self):
        cleaned_data = super().clean()
        inicio = cleaned_data.get("horario_inicio")
        fin = cleaned_data.get("horario_fin")

        if inicio and fin:
            if inicio >= fin:
                raise forms.ValidationError(
                    "La hora de inicio debe ser menor que la hora de fin."
                )

        return cleaned_data


# ---------------------------------------
# CAMBIAR CONTRASEÑA
# --------------------------------------
class CambiarPasswordForm(forms.Form):
    password_actual = forms.CharField(
        label="Contraseña actual",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    password_nueva = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    confirmar_password = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    def __init__(self, usuario, *args, **kwargs):
        self.usuario = usuario
        super().__init__(*args, **kwargs)

    def clean_password_actual(self):
        password_actual = self.cleaned_data.get("password_actual")

        if not check_password(password_actual, self.usuario.password):
            raise forms.ValidationError("❌ Contraseña actual incorrecta")

        return password_actual

    def clean(self):
        cleaned_data = super().clean()
        nueva = cleaned_data.get("password_nueva")
        confirmar = cleaned_data.get("confirmar_password")

        if nueva and confirmar and nueva != confirmar:
            raise forms.ValidationError("❌ Las contraseñas no coinciden")

        if nueva and len(nueva) < 6:
            raise forms.ValidationError(
                "La contraseña debe tener al menos 6 caracteres"
            )

        return cleaned_data

    def save(self):
        nueva_password = self.cleaned_data["password_nueva"]
        self.usuario.password = make_password(nueva_password)
        self.usuario.save()
