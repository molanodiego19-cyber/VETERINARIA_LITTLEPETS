from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from notificacion.models import Notificacion
from notificacion.forms import NotificacionForm


class NotificacionListView(ListView):
    model = Notificacion
    template_name = "panel/notificacion/list.html"
    context_object_name = "notificaciones"


class NotificacionCreateView(CreateView):
    model = Notificacion
    form_class = NotificacionForm
    template_name = "panel/notificacion/form.html"
    success_url = reverse_lazy("panel:panel_notificacion_list")


class NotificacionUpdateView(UpdateView):
    model = Notificacion
    form_class = NotificacionForm
    template_name = "panel/notificacion/form.html"
    success_url = reverse_lazy("panel:panel_notificacion_list")


class NotificacionDeleteView(DeleteView):
    model = Notificacion
    template_name = "panel/notificacion/delete.html"
    success_url = reverse_lazy("panel:panel_notificacion_list")
