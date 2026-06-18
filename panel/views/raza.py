from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from mascota.models import Raza
from mascota.forms import RazaForm


class RazaListView(ListView):
    model = Raza
    template_name = "panel/raza/list.html"
    context_object_name = "razas"


class RazaCreateView(CreateView):
    model = Raza
    form_class = RazaForm
    template_name = "panel/raza/form.html"
    success_url = reverse_lazy("panel:panel_raza_list")


class RazaUpdateView(UpdateView):
    model = Raza
    form_class = RazaForm
    template_name = "panel/raza/form.html"
    success_url = reverse_lazy("panel:panel_raza_list")


class RazaDeleteView(DeleteView):
    model = Raza
    template_name = "panel/raza/delete.html"
    success_url = reverse_lazy("panel:panel_raza_list")
