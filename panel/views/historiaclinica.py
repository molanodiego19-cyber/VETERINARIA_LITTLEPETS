from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from citas.models import HistoriaClinica
from citas.forms import HistoriaClinicaForm


class HistoriaListView(ListView):
    model = HistoriaClinica
    template_name = "panel/historiaclinica/historiaclinica_list.html"
    context_object_name = "historias"


class HistorialCreateView(CreateView):
    model = HistoriaClinica
    form_class = HistoriaClinicaForm
    template_name = "panel/historiaclinica/historiaclinica_form.html"
    success_url = reverse_lazy("panel:panel_historiaclinica_list")


class HistorialUpdateView(UpdateView):
    model = HistoriaClinica
    form_class = HistoriaClinicaForm
    template_name = "panel/historiaclinica/historiaclinica_form.html"
    success_url = reverse_lazy("panel:panel_historiaclinica_list")


class HistorialDeleteView(DeleteView):
    model = HistoriaClinica
    template_name = "panel/historiaclinica/historiaclinica_confirm_delete.html"
    success_url = reverse_lazy("panel:panel_historiaclinica_list")
