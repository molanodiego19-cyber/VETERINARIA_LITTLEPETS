from django import forms
from .models import Especialidad, HorarioVeterinario, BloqueoAgenda


class EspecialidadForm(forms.ModelForm):
    class Meta:
        model = Especialidad
        fields = ["nombre", "descripcion", "activo"]
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre de la especialidad",
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Descripción breve",
                }
            ),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class HorarioVeterinarioForm(forms.ModelForm):
    class Meta:
        model = HorarioVeterinario
        fields = [
            "veterinario",
            "dias_semana",
            "hora_inicio",
            "hora_fin",
            "intervalo_min",
            "activo",
            "fecha_desde",
            "fecha_hasta",
        ]
        widgets = {
            "veterinario": forms.Select(attrs={"class": "form-select"}),
            "hora_inicio": forms.TimeInput(
                format="%H:%M", attrs={"type": "time", "class": "form-control"}
            ),
            "hora_fin": forms.TimeInput(
                format="%H:%M", attrs={"type": "time", "class": "form-control"}
            ),
            "intervalo_min": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "placeholder": "Intervalo en minutos",
                }
            ),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "fecha_desde": forms.DateInput(
                format="%Y-%m-%d", attrs={"type": "date", "class": "form-control"}
            ),
            "fecha_hasta": forms.DateInput(
                format="%Y-%m-%d", attrs={"type": "date", "class": "form-control"}
            ),
        }


class BloqueoAgendaForm(forms.ModelForm):
    class Meta:
        model = BloqueoAgenda
        fields = [
            "veterinario",
            "fecha_inicio",
            "fecha_fin",
            "motivo",
            "tipo",
            "todo_el_dia",
            "recurrente",
            "creado_por",
        ]
        widgets = {
            "veterinario": forms.Select(attrs={"class": "form-select"}),
            "fecha_inicio": forms.DateInput(
                format="%Y-%m-%d", attrs={"type": "date", "class": "form-control"}
            ),
            "fecha_fin": forms.DateInput(
                format="%Y-%m-%d", attrs={"type": "date", "class": "form-control"}
            ),
            "motivo": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Motivo del bloqueo"}
            ),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "todo_el_dia": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "recurrente": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "creado_por": forms.HiddenInput(),  # se puede setear automáticamente en la vista
        }
