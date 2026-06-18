from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from citas.models import Consulta
from citas.forms import ConsultaForm


class ConsultaListView(ListView):
    model = Consulta
    template_name = "panel/consulta/consulta_list.html"
    context_object_name = "consultas"


class ConsultaCreateView(CreateView):
    model = Consulta
    form_class = ConsultaForm
    template_name = "panel/consulta/consulta_form.html"
    success_url = reverse_lazy("panel:panel_consulta_list")


class ConsultaUpdateView(UpdateView):
    model = Consulta
    form_class = ConsultaForm
    template_name = "panel/consulta/consulta_form.html"
    success_url = reverse_lazy("panel:panel_consulta_list")


class ConsultaDeleteView(DeleteView):
    model = Consulta
    template_name = "panel/consulta/consulta_confirm_delete.html"
    success_url = reverse_lazy("panel:panel_consulta_list")
