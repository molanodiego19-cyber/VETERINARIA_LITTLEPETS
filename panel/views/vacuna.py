from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from citas.models import Vacuna
from citas.forms import VacunaForm


class VacunaListView(ListView):
    model = Vacuna
    template_name = "panel/vacuna/list.html"
    context_object_name = "vacunas"


class VacunaCreateView(CreateView):
    model = Vacuna
    form_class = VacunaForm
    template_name = "panel/vacuna/form.html"
    success_url = reverse_lazy("panel:panel_vacuna_list")


class VacunaUpdateView(UpdateView):
    model = Vacuna
    form_class = VacunaForm
    template_name = "panel/vacuna/form.html"
    success_url = reverse_lazy("panel:panel_vacuna_list")


class VacunaDeleteView(DeleteView):
    model = Vacuna
    template_name = "panel/vacuna/delete.html"
    success_url = reverse_lazy("panel:panel_vacuna_list")
