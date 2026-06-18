from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from notificacion.models import PlantillaNotificacion
from notificacion.forms import PlantillaNotificacionForm


class PlantillaNotificacionListView(ListView):
    model = PlantillaNotificacion
    template_name = "panel/plantilla_notificacion/list.html"
    context_object_name = "plantillas"


class PlantillaNotificacionCreateView(CreateView):
    model = PlantillaNotificacion
    form_class = PlantillaNotificacionForm
    template_name = "panel/plantilla_notificacion/form.html"
    success_url = reverse_lazy("panel:panel_plantilla_list")


class PlantillaNotificacionUpdateView(UpdateView):
    model = PlantillaNotificacion
    form_class = PlantillaNotificacionForm
    template_name = "panel/plantilla_notificacion/form.html"
    success_url = reverse_lazy("panel:panel_plantilla_list")


class PlantillaNotificacionDeleteView(DeleteView):
    model = PlantillaNotificacion
    template_name = "panel/plantilla_notificacion/delete.html"
    success_url = reverse_lazy("panel:panel_plantilla_list")
