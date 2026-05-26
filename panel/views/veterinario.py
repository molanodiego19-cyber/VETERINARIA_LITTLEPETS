from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth import get_user_model
from usuarios.models import  Veterinario
from usuarios.forms import VeterinarioCompletoForm,VeterinarioUpdateForm
from django.http import JsonResponse
from citas.models import Servicio


from django.views import View
from django.shortcuts import render, redirect, get_object_or_404

class VeterinarioListView(ListView):
    model = Veterinario
    template_name = 'panel/veterinario/list.html'
    context_object_name = 'veterinarios'


class VeterinarioCreateView(CreateView):
    model = Veterinario
    form_class = VeterinarioCompletoForm
    template_name = 'panel/veterinario/form.html'
    success_url = reverse_lazy('panel:panel_veterinario_list')


class VeterinarioUpdateView(UpdateView):
    model = Veterinario
    form_class = VeterinarioUpdateForm
    template_name = 'panel/veterinario/form.html'
    success_url = reverse_lazy('panel:panel_veterinario_list')

class VeterinarioDeleteView(View):
    def post(self, request, pk):
        veterinario = get_object_or_404(Veterinario, pk=pk)

        veterinario.usuario.estado = 'Inactivo'
        veterinario.usuario.save()

        return redirect('panel:panel_veterinario_list')
#----------------------------------
def cargar_servicios(request):
    especialidad_id = request.GET.get('especialidad_id')

    if not especialidad_id:
        return JsonResponse([], safe=False)

    servicios = Servicio.objects.filter(
        especialista_required_id=especialidad_id
    ).values('id', 'nombre')

    return JsonResponse(list(servicios), safe=False)