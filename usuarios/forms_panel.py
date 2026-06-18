from django import forms
from usuarios.models import Propietario, Veterinario
from django.contrib.auth.hashers import check_password, make_password
from datetime import date
import re




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
