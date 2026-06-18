from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from citas.models import Vacunacion
from citas.forms import VacunacionForm


class VacunacionListView(ListView):
    model = Vacunacion
    template_name = "panel/vacunacion/list.html"
    context_object_name = "vacunaciones"


class VacunacionCreateView(CreateView):
    model = Vacunacion
    form_class = VacunacionForm
    template_name = "panel/vacunacion/form.html"
    success_url = reverse_lazy("panel:panel_vacunacion_list")


class VacunacionUpdateView(UpdateView):
    model = Vacunacion
    form_class = VacunacionForm
    template_name = "panel/vacunacion/form.html"
    success_url = reverse_lazy("panel:panel_vacunacion_list")


class VacunacionDeleteView(DeleteView):
    model = Vacunacion
    template_name = "panel/vacunacion/delete.html"
    success_url = reverse_lazy("panel:panel_vacunacion_list")
