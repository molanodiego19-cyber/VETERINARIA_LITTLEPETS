from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from mascota.models import Especie
from mascota.forms import EspecieForm


class EspecieListView(ListView):
    model = Especie
    template_name = "panel/especie/list.html"
    context_object_name = "especies"


class EspecieCreateView(CreateView):
    model = Especie
    form_class = EspecieForm
    template_name = "panel/especie/form.html"
    success_url = reverse_lazy("panel:panel_especie_list")


class EspecieUpdateView(UpdateView):
    model = Especie
    form_class = EspecieForm
    template_name = "panel/especie/form.html"
    success_url = reverse_lazy("panel:panel_especie_list")


class EspecieDeleteView(DeleteView):
    model = Especie
    template_name = "panel/especie/delete.html"
    success_url = reverse_lazy("panel:panel_especie_list")
