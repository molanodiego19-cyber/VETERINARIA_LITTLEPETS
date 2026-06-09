from django import forms
from .models import Especie, Raza


class EspecieForm(forms.ModelForm):
    class Meta:
        model = Especie
        fields = ["nombre", "descripcion"]


class RazaForm(forms.ModelForm):
    class Meta:
        model = Raza
        fields = ["nombre", "tipo_especie"]
