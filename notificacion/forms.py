from django import forms
from .models import PlantillaNotificacion, Notificacion


class PlantillaNotificacionForm(forms.ModelForm):
    class Meta:
        model = PlantillaNotificacion
        fields = ["nombre", "canal", "asunto_plantilla", "cuerpo_plantilla", "activo"]

        widgets = {
            "cuerpo_plantilla": forms.Textarea(attrs={"rows": 5}),
        }


class NotificacionForm(forms.ModelForm):
    class Meta:
        model = Notificacion
        fields = [
            "usuario",
            "plantilla",
        ]

        widgets = {
            "usuario": forms.Select(attrs={"class": "form-select"}),
            "plantilla": forms.Select(attrs={"class": "form-select"}),
        }
