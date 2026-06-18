from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from veterinarioapp.models import Especialidad
from veterinarioapp.forms import EspecialidadForm


class EspecialidadListView(ListView):
    model = Especialidad
    template_name = "panel/especialidad/list.html"
    context_object_name = "especialidades"


class EspecialidadCreateView(CreateView):
    model = Especialidad
    form_class = EspecialidadForm
    template_name = "panel/especialidad/form.html"
    success_url = reverse_lazy("panel:panel_especialidad_list")


class EspecialidadUpdateView(UpdateView):
    model = Especialidad
    form_class = EspecialidadForm
    template_name = "panel/especialidad/form.html"
    success_url = reverse_lazy("panel:panel_especialidad_list")


class EspecialidadDeleteView(DeleteView):
    model = Especialidad
    template_name = "panel/especialidad/delete.html"
    success_url = reverse_lazy("panel:panel_especialidad_list")
